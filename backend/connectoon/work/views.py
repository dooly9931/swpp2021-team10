from django.http import HttpResponse, HttpResponseNotAllowed
import json
import re
import operator
from django.http.response import HttpResponseBadRequest, JsonResponse
from json.decoder import JSONDecodeError
from django.forms.models import model_to_dict
from django.core.files import File

from work.models import Work
from review.models import Review, ReviewUserLike
from tag.models import Tag
from user.models import UserTagFav
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Q

import make_profile

def work_id(request, id):
    try:
        work = Work.objects.get(id = id)
    except Work.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        tag_name = [tag.name for tag in work.tags.all()]
        artist_name = [artist.name for artist in work.artists.all()]
        work_json = {
            "id": work.id, "title": work.title, "description": work.description, "link": work.link,
            "thumbnail_picture": work.thumbnail_picture, "platform_id": work.platform_id, "year": work.year, 
            "tags": tag_name, "artists": artist_name, "score_avg": work.score_avg,
        }
        return JsonResponse(work_json, status = 200)
    else:
        return HttpResponseNotAllowed(['GET'])


def work_id_review(request, id):
    user_class = get_user_model()

    try:
        work = Work.objects.get(id = id)
    except Work.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        reviews = Review.objects.filter(work = id)
        response_dict = []

        request_user = request.user

        for review in reviews:
            work = Work.objects.get(id=review.work_id)
            work_artist_name = [artist.name for artist in work.artists.all()]
            work_dict = {
                "id": work.id, "title": work.title, "thumbnail_picture": work.thumbnail_picture,
                "platform_id": work.platform_id, "year": work.year, "artists": work_artist_name
            }
            author = user_class.objects.get(id=review.author_id)
            author_dict = {
                "id": author.id, "username": author.username, "email": author.email, # "profile_picture": author.profile_picture
            }

            clickedLikeReview = False
            if request_user.is_authenticated and ReviewUserLike.objects.filter(user = request_user, review = review):
                clickedLikeReview = True
            
            response_dict.append({
                "id": review.id, "title": review.title, "content": review.content, "score": review.score, "likes": review.likes,
                "work": work_dict, "author": author_dict, "clickedLike": clickedLikeReview
            })
        
        return JsonResponse({ "reviews": response_dict }, status=200, safe = False)


    elif request.method == 'POST':
        request_user = request.user
        if not request_user.is_authenticated:
            return HttpResponse(status = 401)

        try:
            body = json.loads(request.body.decode())
            title = body['title']
            content = body['content']
            score = body['score']
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        
        review = Review(author = request_user, work = work, title = title, content = content, score = score)
        review.save()
        
        work.review_num = work.review_num + 1
        work.score_sum = work.score_sum + float(score)
        work.score_avg = work.score_sum / work.review_num
        work.save()

        review_json = model_to_dict(review)
        return JsonResponse(review_json, status=201) 
    
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


def work_main(request):
    if request.method == 'GET':
        requestWorks = request.GET.getlist('requestWorks[]', None)

        most_reviewed_work_objects = Work.objects.all().order_by('-review_num')
        most_reviewed_works = []
        request_range = json.loads(requestWorks[0])
        max_idx = len(most_reviewed_work_objects)
        for work in most_reviewed_work_objects[min(max_idx, request_range[0]):min(max_idx, request_range[1])]:
            artist_name = [artist.name for artist in work.artists.all()]
            most_reviewed_works.append({
                "id": work.id, "title": work.title, "thumbnail_picture": work.thumbnail_picture, "platform_id": work.platform_id, 
                "year": work.year, "artists": artist_name, "score_avg": work.score_avg, "completion": work.completion,
            })
        most_reviewed_works_json = json.dumps(list(most_reviewed_works))

        highest_rated_work_objects = Work.objects.all().order_by('-score_avg')
        highest_rated_works = []
        request_range = json.loads(requestWorks[1])
        max_idx = len(highest_rated_work_objects)
        for work in highest_rated_work_objects[min(max_idx, request_range[0]):min(max_idx, request_range[1])]:
            artist_name = [artist.name for artist in work.artists.all()]
            highest_rated_works.append({
                "id": work.id, "title": work.title, "thumbnail_picture": work.thumbnail_picture, "platform_id": work.platform_id, 
                "year": work.year, "artists": artist_name, "score_avg": work.score_avg, "completion": work.completion,
            })
        highest_rated_works_json = json.dumps(list(highest_rated_works))

        return JsonResponse({"worklists": [{"title" : "Most reviewed works", "works": most_reviewed_works_json}, {"title" : "Highest rated works", "works": highest_rated_works_json}]}, status = 200)
    else:
        return HttpResponseNotAllowed(['GET'])


def work_recommend(request):  # TODO
    request_user = request.user
    if request.method == 'GET':
        if not request_user.is_authenticated:
            return HttpResponse(status=401)
            
        requestWorks = request.GET.getlist('requestWorks[]', None)

        tag_list = [Tag.objects.get(id=tag['tag_id']) for tag in request_user.user_tag.all().values()]

        if len(tag_list) == 0:
            tag_work_title = "Check favorite tags to get tag-based recommendation."
            tag_based_work = []

        else:
            tag_work_title = "Genre-based recommendation"
            tag_based_work_name_list = [work for work in Work.objects.filter(tags__in=tag_list).values()]
            
            request_range = json.loads(requestWorks[0])
            max_idx = len(tag_based_work_name_list)
            tag_based_work = list(map(lambda work: {'title': work['title'], 'thumbnail_picture': work['thumbnail_picture'],
            'description': work['description'], 'year': work['year'], 'link': work['link'],
            'completion': work['completion'], 'score_avg': work['score_avg'], 'review_num': work['review_num'],
            'platform_id': work['platform_id'],
            'artists': [artist.name for artist in Work.objects.get(title=work['title']).artists.all()],
            'id': work['id']}, tag_based_work_name_list[min(max_idx, request_range[0]):min(max_idx, request_range[1])]))

        review_list = [Review.objects.get(id=review['id']) for review in Review.objects.filter(author=request_user).values()]
        review_list.reverse()
        review_list = review_list[:5]

        if len(review_list) == 0:
            review_work_title = "Leave reviews to get review-based recommendation."
            review_based_work = []

        else:
            tag_dic = {}
            for review in review_list:  
                for tag in review.work.tags.all():
                    try:
                        tag_dic[tag.id] += 1
                    except:
                        tag_dic[tag.id] = 1
            
            sorted_tag_list = list(sorted(tag_dic.items(), key=operator.itemgetter(0), reverse=True))[:3]
            tag_list = [Tag.objects.get(id=tag[0]) for tag in sorted_tag_list]

            for review in review_list:
                if tag_list[0] in review.work.tags.all():
                    review_work_title = "Works similar to \'" + review.work.title + "\' you reviewed recently."
                    break

            review_based_work_name_list = [work for work in Work.objects.filter(tags__in=tag_list).values()]
            
            request_range = json.loads(requestWorks[1])
            max_idx = len(review_based_work_name_list)
            review_based_work = list(map(lambda work: {'title': work['title'], 'thumbnail_picture': work['thumbnail_picture'],
            'description': work['description'], 'year': work['year'], 'link': work['link'],
            'completion': work['completion'], 'score_avg': work['score_avg'], 'review_num': work['review_num'],
            'platform_id': work['platform_id'],
            'artists': [artist.name for artist in Work.objects.get(title=work['title']).artists.all()],
            'id': work['id']}, review_based_work_name_list[min(max_idx, request_range[0]):min(max_idx, request_range[1])]))

        return JsonResponse({"worklists": [{"title" : tag_work_title, "works": tag_based_work}, {"title" : review_work_title, "works": review_based_work}]}, status = 200, safe=False)
    else:
        return HttpResponseNotAllowed(['GET'])

def work_search(request):  # TODO
    if request.method == 'GET':
        keyword = request.GET.get('q', None)
        keytag = request.GET.get('tags', None)
        
        return_work_list = [[], []]
        if keyword == '' and keytag == '':
            return JsonResponse(return_work_list, safe=False)
        
        tag_list = [Tag.objects.get(name=tagname) for tagname in keytag.split('$')[1:]]
        tag_filtered_work = Work.objects
        for tag in tag_list:
            tag_filtered_work = tag_filtered_work.filter(tags__in=[tag]).distinct()

        if len(tag_list) == 0:
            work_title_list = [work for work in Work.objects.filter(Q(title__contains=keyword)).values()]
            work_artist_list = [work for work in Work.objects.filter(Q(artists__name__contains=keyword)).values()]
        else:
            work_title_list = [work for work in tag_filtered_work.filter(Q(title__contains=keyword)).values()]
            work_artist_list = [work for work in tag_filtered_work.filter(Q(artists__name__contains=keyword)).values()]

        requestWorks = request.GET.getlist('requestWorks[]', None)
        request_range = json.loads(requestWorks[0])
        max_idx = len(work_title_list)
        return_work_list[0] = list(map(lambda work: {'title': work['title'], 'thumbnail_picture': work['thumbnail_picture'],
        'description': work['description'], 'year': work['year'], 'link': work['link'],
        'completion': work['completion'], 'score_avg': work['score_avg'], 'review_num': work['review_num'],
        'platform_id': work['platform_id'],
        'artists': [artist.name for artist in Work.objects.get(title=work['title']).artists.all()],
        'id': work['id']}, work_title_list[min(max_idx, request_range[0]):min(max_idx, request_range[1])]))

        request_range = json.loads(requestWorks[1])
        max_idx = len(work_artist_list)
        return_work_list[1] = list(map(lambda work: {'title': work['title'], 'thumbnail_picture': work['thumbnail_picture'],
        'description': work['description'], 'year': work['year'], 'link': work['link'],
        'completion': work['completion'], 'score_avg': work['score_avg'], 'review_num': work['review_num'],
        'platform_id': work['platform_id'],
        'artists': [artist.name for artist in Work.objects.get(title=work['title']).artists.all()],
        'id': work['id']}, work_artist_list[min(max_idx, request_range[0]):min(max_idx, request_range[1])]))
        
        return JsonResponse(return_work_list, safe=False)
    else:
        return HttpResponseNotAllowed(['GET'])

def work_image(request, id):  # TODO
    try:
        work = Work.objects.get(id = id)
    except Work.DoesNotExist:
        return HttpResponse(status=404)
    
    if request.method == 'GET':
        request_user = request.user

        if request_user.profile_picture:
            new_image = make_profile.make_image(request_user.profile_picture.url, work.thumbnail_picture)
            request_user.transferred_picture.save('new_image.jpg', File(new_image), save=True)
            request_user.save()

        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(['GET'])
