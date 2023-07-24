from Accounts.models import CustomUser
from Accounts.serializers import UserSerializer, PublicUserSerializer
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
    User = PublicUserSerializer()
    created_at = serializers.DateTimeField()

    class Meta:
        model = Comment
        fields = '__all__'


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Announcement
        fields = ('__all__')
        lookup_field = 'classroom_id'

    def create(self, request):
        data = request.data
        try:
            ancmnt = Announcement()
            # created_by = CustomUser.objects.get(email=request.user)
            ancmnt.created_by = request.user
            ancmnt.announcement = data['announcement']
            ancmnt.classroom = Classroom.objects.get(id=data['classroom'],teacher=request.user)
            ancmnt.save()

            return ancmnt
        except Exception as e:
            print(e)
            return None


class PostSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        max_length=None, use_url=True
    )
    user = PublicUserSerializer()
    comments = CommentSerializer(many=True)

    class Meta:
        model = Post
        fields = '__all__'


    def to_representation(self, instance):
        # Call the parent class's to_representation method
        data = super().to_representation(instance)
        
        # Reformat the comments as a dictionary, keyed by comment ID
        comments_dict = {comment['id']: comment for comment in data.pop('comments')}

        # Add the comments to the post data using the comment IDs as keys
        data['comments'] = comments_dict

        return data
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        file_url = obj.fingerprint.url
        return request.build_absolute_uri(file_url)

    def post_file_url(self, obj):
        request = self.context.get('request')
        file_url = obj.fingerprint.url
        return request.build_absolute_uri(file_url)



class AllClassRoomSerializer(serializers.ModelSerializer):

    # posts = PostSerializer(many=True)
    teacher = serializers.CharField(source='teacher.name', read_only=True)
    # students = UserSerializer(many=True)

    class Meta:
        model = Classroom
        fields = ('__all__')
        lookup_field = 'slug'

  
    def create(self, request):
        data = request.data
        classroom = Classroom()
        teacher = CustomUser.objects.get(email=request.user)
        classroom.teacher = teacher
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




class ClassRoomSerializer(serializers.ModelSerializer):

    # posts = PostSerializer(many=True)
    teacher = UserSerializer()
    students = UserSerializer(many=True)
    # announcements = AnnouncementSerializer(many=True)

    class Meta:
        model = Classroom
        fields = ('__all__')
        lookup_field = 'slug'

    # def to_representation(self, instance):
    #     # Call the parent class's to_representation method
    #     data = super().to_representation(instance)

    #     # Reformat the posts as a dictionary, keyed by post ID
    #     posts_dict = {post['id']: post for post in data.pop('posts')}


    #     data['posts'] = posts_dict

    #     return data

class AttendanceSerializer(serializers.ModelSerializer):
    students = serializers.CharField(source='students.name', read_only=True)

    class Meta:
        model = Attendance
        fields = ('__all__')
    
class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        max_length=None, use_url=True
    )
    created_by = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = '__all__'
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        file_url = obj.fingerprint.url
        return request.build_absolute_uri(file_url)

    def post_file_url(self, obj):
        request = self.context.get('request')
        file_url = obj.fingerprint.url
        return request.build_absolute_uri(file_url)

class AssignmentSerializer(serializers.ModelSerializer):
    submissions = AssignmentSubmissionSerializer(read_only=True, many=True)
    file = serializers.FileField(
        max_length=None, use_url=True
    )
    
    class Meta:
        model = Assignment
        fields = '__all__'

    def get_file_url(self, obj):
        request = self.context.get('request')
        file_url = obj.fingerprint.url
        return request.build_absolute_uri(file_url)

    def post_file_url(self, obj):
        request = self.context.get('request')
        file_url = obj.fingerprint.url
        return request.build_absolute_uri(file_url)


class AssignmentStudentSerializer(serializers.ModelSerializer):
    submissions = AssignmentSubmissionSerializer(read_only=True, many=True)
    file = serializers.FileField(
        max_length=None, use_url=True
    )
    
    class Meta:
        model = Assignment
        fields = '__all__'

    def get_file_url(self, obj):
        request = self.context.get('request')
        file_url = obj.fingerprint.url
        return request.build_absolute_uri(file_url)

    def post_file_url(self, obj):
        request = self.context.get('request')
        file_url = obj.fingerprint.url
        return request.build_absolute_uri(file_url)

    def to_representation(self, instance):
        # Call the parent class's to_representation method
        data = super().to_representation(instance)
        try:
            request = self.context.get('request')
            data["submissions"] = instance.submissions.count()
            assignment_sub = instance.submissions.filter(created_by=request.user).first()
            if assignment_sub:
                data["submitted"] = True
                data["score"] = "Pending"
                data["remarks"] = ""
                if assignment_sub.score:
                    data["score"] = assignment_sub.score
                if assignment_sub.remarks:
                    data["remarks"] = assignment_sub.remarks
        except:
            pass

        return data
