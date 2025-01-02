from celery.result import AsyncResult

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .tasks import analyizer


@api_view(['POST'])
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
def status_task(request,task_id):
    result = AsyncResult(task_id)
    return Response({"task_id": task_id,
                     "status" : result.state,
                     "Result": result.result
                     })