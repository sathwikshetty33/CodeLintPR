import http
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
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


from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPI(APIView):
    authentication_classes = []  # Explicitly allow unauthenticated access
    permission_classes = []  # No permission checks for login

    def post(self, request):
        try:
            # Print debugging information
            print('Login request received')

            # Use request.data directly for DRF
            username = request.data.get('username')
            password = request.data.get('password')

            # Validate input
            if not username or not password:
                return Response({
                    "error": "Username and password are required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Authenticate user
            user = authenticate(username=username, password=password)

            if user is None:
                print(f"Authentication failed for user: {username}")
                return Response({
                    "error": "Invalid username or password"
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Create or get existing token
            token, created = Token.objects.get_or_create(user=user)

            print(f"Login successful for user: {username}")
            return Response({
                "token": token.key,
                "user_id": user.id,
                "username": user.username
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Exception in login API: {str(e)}")
            return Response({
                "error": f"Server error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
