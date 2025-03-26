from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    mobile_number = models.CharField(max_length=10, blank=True, null=True)
    last_name = models.CharField('last name',max_length=150,blank=True, null=True)
    user_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    