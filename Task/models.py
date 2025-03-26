from django.db import models
import uuid
from Accounts.models import User
from django.utils import timezone
from .config import TASK_STATUS, TASK_TYPE

class Task(models.Model):
    task_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(User, related_name="assigned")
    name = models.TextField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    completed_at = models.DateTimeField(null=True)
    task_type = models.CharField(max_length = 20,choices = TASK_STATUS,default = 'RED')
    task_status = models.CharField(max_length = 20,choices = TASK_TYPE,default = 'TODO')