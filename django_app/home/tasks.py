import eventlet
eventlet.monkey_patch()
from celery import Celery,shared_task

from .utils.github import any_pr

app = Celery('django_app')
app.config_from_object('django.cong:settings', namespace="Celery")

@shared_task
def analyizer(repo_url, pr_num, githubtoken=None):
    result = any_pr(repo_url, pr_num, githubtoken)
    return result