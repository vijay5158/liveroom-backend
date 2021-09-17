from django.db import models
from django.contrib.auth.models import User
import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

def file_upload_path(instance, filename):
    return 'user/'+ str(instance.email) + '/' + filename

class CustomUser(AbstractUser):
    username = None
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField('Email Address', unique=True)
    mobile = models.CharField(max_length=14, unique=True)
    profile_img = models.ImageField(upload_to=file_upload_path, blank=True,null=True)
    is_student = models.BooleanField(null=True, blank=True)
    is_teacher = models.BooleanField(null=True, blank=True)
    token = models.CharField(max_length=400)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile', 'first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField('Email Address', unique=True)
    mobile = models.CharField(max_length=14, unique=True)
    concern = models.CharField(max_length=500)

    def __str__(self):
        return self.email



