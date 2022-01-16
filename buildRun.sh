#!/bin/bash

echo 'docker stop frontend_container'
docker stop frontend_container

echo 'docker stop backend_container'
docker stop backend_container

echo 'docker system prune'
docker system prune

echo 'docker volume prune'
docker volume prune

echo 'cd frontend/connectoon'
cd frontend/connectoon

echo 'docker build -t frontend .'
docker build -t frontend .

echo "docker run -p 443:443 -v '/etc/letsencrypt:/etc/letsencrypt' --rm -d --name frontend_container frontend"
docker run -p 443:443 -v '/etc/letsencrypt:/etc/letsencrypt' --rm -d --name frontend_container frontend

echo 'cd ../../backend/connectoon'
cd ../../backend/connectoon

echo 'docker build -t backend .'
docker build -t backend .

echo 'docker run -it --rm -d -p 0.0.0.0:8000:8000 --name backend_container backend:latest'
docker run -it --rm -d -p 0.0.0.0:8000:8000 --name backend_container backend:latest