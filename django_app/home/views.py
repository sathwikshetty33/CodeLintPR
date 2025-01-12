import http

from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from celery.result import AsyncResult
from django.contrib.auth import authenticate, user_logged_in
from django.core.serializers import serialize
from .serializer import *
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .serializer import loginSearializer
from .tasks import analyizer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_task(request):
    data = request.data
    repo_url = data.get('repo_url')
    pr_num = data.get('pr_num')
    github_token = data.get('github_token')
    task = analyizer.delay(repo_url, pr_num, github_token)
    return Response({"task_id": task.id,
                     "status" : "Task Started",

              })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def status_task(request,task_id):
    result = AsyncResult(task_id)
    return Response({"task_id": task_id,
                     "status" : result.state,
                     "Result": result.result
                     })

class loginapi(APIView):
    def post(self, request):
        data = request.data
        serializer=loginSearializer(data=data)
        if not serializer.is_valid():
            return Response({"some error":serializer.errors})
        username = serializer.data['username']
        password = serializer.data['password']
        us = authenticate(username=username,password=password)
        if us is None:
            return  Response({
                "error" : "Invalid username and password"
            })
        token,_ = Token.objects.get_or_create(user=us)
        return Response({
            "token" : token.key
        })

class registerapi(APIView):
    def post(self, request):
        data = request.data
        serializer = loginSearializer(data=data)
        if not serializer.is_valid():
            return Response({"some error": serializer.errors})

        if User.objects.filter(username=serializer.data['username']).exists():
            return Response({
                "error" : "username already exsists"
            })
            # Create new user
        try:
            user = User.objects.create_user(  # Use create_user instead of create
                username=serializer.data['username'],
                password=serializer.data['password']
            )
            return Response({
                "status": "success"
            })
        except Exception as e:
            return Response({
                "error": "Failed to create user"
            })
