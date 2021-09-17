import json

import channels.layers
from Accounts.models import CustomUser
from asgiref.sync import async_to_sync
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
# from rest_framework_simplejwt.authentication import JWTAuthentication
# Create your views here.
# from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
# from rest_framework.parsers import JSONParse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.status import (HTTP_201_CREATED, HTTP_400_BAD_REQUEST,
                                   HTTP_406_NOT_ACCEPTABLE)
from rest_framework.views import APIView

from .models import Announcement, Classroom, Comment, Post
from .serializers import (AnnouncementSerializer, ClassRoomSerializer,
                          CommentSerializer, PostSerializer)

# @csrf_exempt


class AnnouncementView(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    queryset = Announcement.objects.all()
    # lookup_field = 'classroom_id'
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    def retrieve(self, request, pk=None):

        queryset = Announcement.objects.filter(classroom__slug=pk)
        serializer = AnnouncementSerializer(queryset, many=True)
        data = serializer.data
        return Response(data, status=status.HTTP_202_ACCEPTED)

    def create(self, request):
        if request.user.is_student:
            return Response(status=HTTP_406_NOT_ACCEPTABLE)
        serializer = AnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            announcement = serializer.create(request)
            channel_layer = channels.layers.get_channel_layer()
            classroom = Classroom.objects.get(id=announcement.classroom.id)
            slug = classroom.slug
            if announcement:
                serialized = AnnouncementSerializer(announcement)
                async_to_sync(channel_layer.group_send)(
                    'class_'+slug,
                    {
                        'type': 'announcement',
                        'announcement': serialized.data
                    }
                )

                return Response(serialized.data, status=HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST)


class ClassroomView(viewsets.ModelViewSet):
    serializer_class = ClassRoomSerializer
    queryset = Classroom.objects.all()
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    def partial_update(self, request, slug):
        classroom = Classroom.objects.get(slug=slug)
        serialized = ClassRoomSerializer(
            classroom, data=request.data, partial=True)
        if serialized.is_valid():
            updated_data = ClassRoomSerializer.partial_update(
                self, instance=classroom, validated_data=request.data)
            if updated_data.lock == True:
                error = {"massage": "Classroom is locked"}
                return Response(error, status=HTTP_406_NOT_ACCEPTABLE)
            return Response(serialized.data, status=status.HTTP_202_ACCEPTED)

    def create(self, request):
        if request.user.is_student:
            return Response(status=HTTP_406_NOT_ACCEPTABLE)
        serializer = ClassRoomSerializer(data=request.data)
        if serializer.is_valid():
            classroom = serializer.create(request)
            if classroom:
                serialised_data = ClassRoomSerializer(classroom)
                return Response(serialised_data.data, status=HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST)

    def list(self, request):
        classes = Classroom.objects.filter(
            Q(teachers__email=request.user.email) | Q(students__email=request.user.email))
        serializer = ClassRoomSerializer(classes, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    # permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        classroom = Classroom.objects.get(id=data['classroom'])
        file = data['file']
        text = data['text']
        channel_layer = channels.layers.get_channel_layer()
        slug = classroom.slug
        file_name = data['file_name']
        post = Post.objects.create(
            user=user, classroom=classroom, text=text, file=file, file_name=file_name)
        serializer = PostSerializer(post, context={"request": request})

        if serializer:
            async_to_sync(channel_layer.group_send)(
                'class_'+slug,
                {
                    'type': 'post_message',
                    'post': serializer.data
                }
            )

            return Response(serializer.data, status=HTTP_201_CREATED)

        return Response(status=HTTP_400_BAD_REQUEST)
    # @xframe_options_exempt

    def list(self, request):
        queryset = Post.objects.all().order_by('-date', '-time')

        slug = request.query_params.get('slug')
        if slug is not None:
            queryset = queryset.filter(classroom__slug=slug)
            serializer = PostSerializer(
                queryset, context={"request": request}, many=True)
            return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    def list(self, request):
        queryset = Comment.objects.all()
        slug = request.query_params.get('slug')
        if slug is not None:
            classroom = Classroom.objects.get(slug=slug)
            queryset = queryset.filter(post__classroom=classroom)
            serializer = CommentSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            serializer = CommentSerializer(queryset, many=True)
            return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        User = request.user
        text = data['text']
        post = Post.objects.get(id=data['post'])
        comment = Comment.objects.create(User=User, post=post, text=text)
        classroom = Classroom.objects.get(id=post.classroom.id)
        channel_layer = channels.layers.get_channel_layer()
        slug = classroom.slug

        serializer = CommentSerializer(comment)

        if serializer:
            async_to_sync(channel_layer.group_send)(
                'class_'+slug,
                {
                    'type': 'comment_message',
                    'comment': serializer.data
                }
            )

            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST)
