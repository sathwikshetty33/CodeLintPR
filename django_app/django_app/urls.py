"""
URL configuration for django_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from . import views
from home.views import *  # Importing specific views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('start-task/', start_task, name='start_task'),  # Removed 'views.' and added trailing slash
    path('task-status/<str:task_id>/', status_task, name='task_status'),  # Defined task_id as a string
    path('home/',views.homes,name='home'),
    path('',views.loginpage,name='loginpage'),
    path('login/',LoginAPI.as_view() ,name='login'),
    path('register/',registerapi.as_view() ,name='register'),
    path('api/',views.api,name='api'),
    path('github-actions-analyze-pr/', github_actions_analyze_pr, name='github-actions-analyze-pr'),
]
