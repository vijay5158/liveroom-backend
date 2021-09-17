from django.db import models
from Accounts.models import CustomUser
import random
import string
from . import utils
from Liveroom import settings


class Classroom(models.Model):
    # info

    class_name = models.CharField(max_length=30)
    subject = models.CharField(max_length=50)
    standard = models.CharField(max_length=30)
    lock = models.BooleanField(default=False, null=True, blank=True)
#     Class_name = models.OneToOneField(Class,on_delete=models.CASCADE, related_name='class_name', default='class_name')
    # Unique slug
    slug = models.SlugField(max_length=40, blank=True)

    # members
    teachers = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, default='teachers', related_name='teachers')
    students = models.ManyToManyField(
        CustomUser, blank=True, related_name='students')

    # time
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return str(self.class_name + " " + self.standard + " " + self.subject)

    def save(self, *args, **kwargs):
        if not self.slug:
            ran = 'abcd'
            S = random.randint(20, 40)  # number of characters in the string.
            while Classroom.objects.filter(slug=ran).count() != 0 or ran == 'abcd':
                ran = ''.join(random.choices(
                    string.ascii_uppercase + string.digits, k=S))
            self.slug = ran
        return super().save(*args, **kwargs)


def file_upload_path(instance, filename):
    return 'class/' + str(instance.user.id) + '/' + str(instance.classroom.subject) + '/' + filename


class Post(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='user')
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, related_name='classroom')
    file_name = models.CharField(max_length=500, default="")
    text = models.TextField(max_length=500, blank=True)
    file = models.FileField(upload_to=file_upload_path, blank=True)

    # time
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    User = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='comment_user')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comment_post')

    text = models.TextField(max_length=500)

    # time
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.text

# Create your models here.


class Announcement(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, null=True, blank=True)
    announcement = models.CharField(max_length=300)

    def __str__(self):
        return str(self.created_by)
