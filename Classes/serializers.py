from Accounts.models import CustomUser
from Accounts.serializers import UserSerializer
from django.db.models import fields
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_202_ACCEPTED,
                                   HTTP_400_BAD_REQUEST,
                                   HTTP_406_NOT_ACCEPTABLE)

from .models import *


class StringSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value




class CommentSerializer(serializers.ModelSerializer):
    User = UserSerializer()
    created_at = serializers.DateTimeField()

    class Meta:
        model = Comment
        fields = '__all__'

# class CombinedPostSerializer(serializers.ModelSerializer):
#     comments = serializers.SerializerMethodField()
    
#     def get_comments(self, obj):
#         comments = obj.comment_post.all()
#         serializer = CommentSerializer(comments, many=True)
#         return serializer.data

#     class Meta:
#         model = Post
#         fields = '__all__'



class AnnouncementSerializer(serializers.ModelSerializer):
    created_by = StringSerializer(many=False)

    class Meta:
        model = Announcement
        fields = ('__all__')
        lookup_field = 'classroom_id'

    def create(self, request):
        data = request.data
        ancmnt = Announcement()
        created_by = CustomUser.objects.get(email=request.user)
        ancmnt.created_by = created_by
        ancmnt.announcement = data['announcement']
        ancmnt.classroom = Classroom.objects.get(id=data['classroom'])
        ancmnt.save()

        return ancmnt


class PostSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        max_length=None, use_url=True
    )
    user = UserSerializer()
    comments = serializers.SerializerMethodField()
    
    def get_comments(self, obj):
        comments = obj.comment_post.all()
        serializer = CommentSerializer(comments, many=True)
        return serializer.data
    
    class Meta:
        model = Post
        fields = '__all__'

    def get_file_url(self, obj):
        request = self.context.get('request')
        file_url = obj.fingerprint.url
        return request.build_absolute_uri(file_url)

    def post_file_url(self, obj):
        request = self.context.get('request')
        file_url = obj.fingerprint.url
        return request.build_absolute_uri(file_url)


class ClassRoomSerializer(serializers.ModelSerializer):
    # teachers = StringSerializer(many=False)
    posts = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()

    def get_posts(self, obj):
        posts = obj.classroom.all()
        serializer = PostSerializer(posts, many=True)
        return serializer.data
    def get_teachers(self, obj):
        # posts = obj.classroom.all()
        serializer = UserSerializer(obj.teachers)
        return serializer.data
    def get_students(self, obj):
        # posts = obj.classroom.all()
        serializer = UserSerializer(obj.students, many=True)
        return serializer.data

    class Meta:
        model = Classroom
        fields = ('__all__')
        lookup_field = 'slug'

    def create(self, request):
        data = request.data
        classroom = Classroom()
        teachers = CustomUser.objects.get(email=request.user)
        classroom.teachers = teachers
        classroom.class_name = data['class_name']
        classroom.subject = data['subject']
        classroom.standard = data['standard']
        classroom.save()

        return classroom

    def partial_update(self, instance, validated_data):
        if instance.lock:
            return instance
        student_id = validated_data['students'][0]

        instance.students.add(student_id)
        return instance


# class CombinedClassSerializer(serializers.ModelSerializer):
#     posts = serializers.SerializerMethodField()
#     teachers = serializers.SerializerMethodField()
#     students = serializers.SerializerMethodField()

#     def get_posts(self, obj):
#         posts = obj.classroom.all()
#         serializer = CombinedPostSerializer(posts, many=True)
#         return serializer.data
#     def get_teachers(self, obj):
#         # posts = obj.classroom.all()
#         serializer = UserSerializer(obj.teachers)
#         return serializer.data
#     def get_students(self, obj):
#         # posts = obj.classroom.all()
#         serializer = CombinedPostSerializer(obj.students, many=True)
#         return serializer.data
    
#     class Meta:
#         model = Classroom
#         fields = '__all__'
#         lookup_field = 'slug'
