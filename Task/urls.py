from django.urls import path
from .views import *

urlpatterns = [
    path('create',CreateTask.as_view()),
    path('edit',EditTask.as_view()),
    path('assign',AssignTask.as_view()),
    path('unassign',UnassignTask.as_view()),
    path('viewassigned',UserTasks.as_view()),
]