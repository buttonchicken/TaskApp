from .models import Task
from rest_framework import serializers

class TaskSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    completed_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    class Meta:
        model = Task
        fields = ['task_id','created_at','name','description','task_status','task_type','completed_at']