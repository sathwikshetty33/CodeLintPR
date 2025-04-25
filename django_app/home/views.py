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
import json
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from home.tasks import analyizer

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_task(request):
    logger.debug("Headers: %s", request.headers)
    logger.debug("Raw Body: %s", request.body)

    # Check Content-Type header
    content_type = request.headers.get('Content-Type')
    logger.debug("Content-Type Header: %s", content_type)

    # Attempt to parse request.data
    data = request.data
    logger.debug("Parsed Data (request.data): %s", data)

    # Fallback to manual JSON parsing if request.data is empty
    if not data:
        try:
            data = json.loads(request.body.decode('utf-8'))
            logger.debug("Manually Parsed Body: %s", data)
        except json.JSONDecodeError as e:
            logger.error("JSON Decode Error: %s", e)
            return Response({"error": "Invalid JSON"}, status=400)

    # Extract parameters
    repo_url = data.get('repo_url')
    pr_num = data.get('pr_num')
    github_token = data.get('github_token')
    logger.debug("repo_url: %s", repo_url)
    logger.debug("pr_num: %s", pr_num)
    logger.debug("github_token: %s", github_token)

    # Validate parameters
    if not repo_url or not pr_num or not github_token:
        logger.error("Missing required parameters")
        return Response({"error": "Missing required parameters"}, status=400)

    # Start the task
    task = analyizer.delay(repo_url, pr_num, github_token)
    return Response({
        "task_id": task.id,
        "status": "Task Started",
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
