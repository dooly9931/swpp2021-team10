# Generated by Django 3.2.6 on 2021-12-14 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_alter_customuser_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='transferred_picture',
            field=models.ImageField(null=True, upload_to='transferred_picture/%Y/%m/%d'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='want_transferred',
            field=models.BooleanField(default=False),
        ),
    ]