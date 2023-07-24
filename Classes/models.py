from django.db import models
from Accounts.models import CustomUser
import random
import string
from . import utils
from Liveroom import settings
import uuid
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

def generate_unique_id():
    return uuid.uuid4()


def post_file_upload_path(instance, filename):
    return 'classes/'  + str(instance.classroom.subject)+'_'+str(instance.classroom.id)+'/posts/' + filename

def assign_file_upload_path(instance, filename):
    return 'classes/'  + str(instance.classroom.subject)+'_'+str(instance.classroom.id)+'/assignments/' + filename

def assign_sub_file_upload_path(instance, filename):
    return 'classes/'  + str(instance.assignment.id)+'/assignments_sub/' + filename


def file_upload_path(instance, filename):
    return 'classes/'  + str(instance.classroom.subject)+'_'+str(instance.classroom.id)+'/posts/' + filename


def class_file_upload_path(instance, filename):
    return 'classes/'  + str(instance.subject)+'_'+str(instance.id)+'/posters/' + filename


class Classroom(models.Model):
    # info

    class_name = models.CharField(max_length=30)
    subject = models.CharField(max_length=50)
    standard = models.CharField(max_length=30)
    lock = models.BooleanField(default=False, null=True, blank=True)
    isVideo = models.BooleanField(default=False, null=True, blank=True)
#     Class_name = models.OneToOneField(Class,on_delete=models.CASCADE, related_name='class_name', default='class_name')
    # Unique slug
    slug = models.SlugField(max_length=40, blank=True)
    poster = models.ImageField(upload_to=class_file_upload_path,blank=True,null=True)
    # members
    teacher = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True,blank=True, related_name='classrooms')
    students = models.ManyToManyField(
        CustomUser, blank=True, related_name='student_classrooms')
    limit = models.IntegerField(default=60)

    # time
    created_at = models.DateTimeField(auto_now_add=True)
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

class Attendance(models.Model):

    students = models.ManyToManyField(CustomUser, blank=True, related_name='attendances')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True,blank=True, related_name='attendances')
    date = models.DateField(auto_now_add=True)    



class Post(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='posts')
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, related_name='posts')
    file_name = models.CharField(max_length=500, default="")
    text = models.TextField(max_length=500, blank=True)
    file = models.FileField(upload_to=post_file_upload_path, blank=True)

    # time
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    User = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')

    text = models.TextField(max_length=500)

    # time
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

# Create your models here.


class Announcement(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, null=True, blank=True,related_name='announcements')
    announcement = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.created_by)

class Assignment(models.Model):
    
    title = models.CharField(max_length=500, default="")
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assignments')
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, null=True, blank=True,related_name='assignments')
    file = models.FileField(upload_to=assign_file_upload_path, blank=True, null=True)
    assignment = models.TextField(null=True)
    start_date = models.DateTimeField(null=True, blank=True,default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.created_by)

class AssignmentSubmission(models.Model):

    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to=assign_sub_file_upload_path, blank=True)
    score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.created_by)
