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
from rest_framework import status, viewsets, generics
from rest_framework.parsers import FormParser, MultiPartParser
# from rest_framework.parsers import JSONParse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.status import (HTTP_201_CREATED, HTTP_400_BAD_REQUEST,
                                   HTTP_406_NOT_ACCEPTABLE)
from rest_framework.views import APIView

from .models import Announcement, Classroom, Comment, Post, Attendance
from .serializers import (AnnouncementSerializer, AllClassRoomSerializer,
                          CommentSerializer, PostSerializer, ClassRoomSerializer, AttendanceSerializer)
# @csrf_exempt
from datetime import date
from Accounts.face_detection import match_face_template
from .permissions import IsRoleStudent, IsRoleTeacher
from rest_framework.pagination import LimitOffsetPagination
from .pagination import PaginationHandlerMixin
from rest_framework.generics import ListAPIView
from django.utils import timezone
from datetime import timedelta, datetime

class Pagination(LimitOffsetPagination):
    default_limit = 10  # The default number of items per page
    max_limit = 100

class AnnouncementView(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    queryset = Announcement.objects.all()
    # lookup_field = 'classroom_id'
    permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    # permission_classes = [AllowAny]

    def retrieve(self, request, pk=None):

        queryset = Announcement.objects.filter(classroom__slug=pk)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # Serialize the paginated queryset
        serializer = self.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

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


class ClassroomDataView(viewsets.ModelViewSet):
    serializer_class = ClassRoomSerializer
    queryset = Classroom.objects.all()
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]

    def get_allowed_methods(self):
        allowed_methods = super().get_allowed_methods()
        allowed_methods.remove('PUT')
        allowed_methods.remove('PATCH')
        allowed_methods.remove('DELETE')
        allowed_methods.remove('POST')
        return allowed_methods    


class ClassroomView(viewsets.ModelViewSet):
    serializer_class = AllClassRoomSerializer
    queryset = Classroom.objects.all()
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    # permission_classes = [AllowAny]

    def partial_update(self, request, slug):
        classroom = Classroom.objects.get(slug=slug)
        if classroom.lock:
            error = {"massage": "Classroom is locked"}
            return Response(error, status=HTTP_406_NOT_ACCEPTABLE)

        if classroom.students.count() >= classroom.limit:
            error = {"massage": "Classroom is full!"}
            return Response(error, status=HTTP_406_NOT_ACCEPTABLE)

        serialized = AllClassRoomSerializer(
            classroom, data=request.data, partial=True)
        if serialized.is_valid():
            updated_data = AllClassRoomSerializer.partial_update(
                self, instance=classroom, validated_data=request.data)
            if updated_data.lock == True:
                error = {"massage": "Classroom is locked"}
                return Response(error, status=HTTP_406_NOT_ACCEPTABLE)
            return Response(serialized.data, status=status.HTTP_202_ACCEPTED)

    def create(self, request):
        if request.user.is_student:
            return Response(status=HTTP_406_NOT_ACCEPTABLE)
        serializer = AllClassRoomSerializer(data=request.data)
        if serializer.is_valid():
            classroom = serializer.create(request)
            if classroom:
                serialised_data = AllClassRoomSerializer(classroom)
                return Response(serialised_data.data, status=HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST)

    def list(self, request):
        classes = Classroom.objects.filter(
            Q(teacher=request.user) | Q(students=request.user))
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(classes, request)
        
        # Serialize the paginated queryset
        serializer = self.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = Pagination
    # permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        files = request.FILES
        classId = data.get('classroom',None)
        file_name = data.get('file_name',None)
        text = data.get('text',None)
        try:
            classroom = Classroom.objects.get(id=classId,teacher=request.user)
            
            if not data or not text or not classId:
                return Response({"message":"Data required!"},status=HTTP_400_BAD_REQUEST)
            channel_layer = channels.layers.get_channel_layer()
            slug = classroom.slug
            file = files.get('file',None)
            if file and file_name:
                post = Post.objects.create(user=user, classroom=classroom, text=text, file=file, file_name=file_name)
            else:
                post = Post.objects.create(user=user, classroom=classroom, text=text)

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
        except Classroom.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)

        return Response(status=HTTP_400_BAD_REQUEST)
    # @xframe_options_exempt

    def list(self, request):
        # queryset = Post.objects.().order_by('-created_at')

        slug = request.query_params.get('slug')
        if slug is not None:
            queryset = Post.objects.filter(classroom__slug=slug).filter(Q(classroom__teacher=request.user) | Q(classroom__students=request.user)).order_by('-created_at')
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            
            # Serialize the paginated queryset
            serializer = self.get_serializer(paginated_queryset, context={"request": request}, many=True)
            post_data = serializer.data
            posts_dict = {post['id']: post for post in post_data}
            return paginator.get_paginated_response(posts_dict)

            # serializer = PostSerializer(
            #     queryset, context={"request": request}, many=True)
            
            # return Response(serializer.data)
        
        return Response([])


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.order_by('-created_at').all()
    permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    # permission_classes = [AllowAny]

    def list(self, request):
        queryset = Comment.objects.order_by('-created_at').all()
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


class AttendanceAPIView(APIView):
    permission_classes=[IsAuthenticated, IsRoleStudent]

    def post(self,request):
        user = request.user

        if not user:
            return Response({'success':False,'msg':'User does not present!'},202)

        if user.is_teacher:
            return Response({'success':False,'msg':'You are a teacher, can not mark attendance'},202)

        if not user.profile_img or not user.face_template:
            return Response({'success':False,'msg':'Cant mark attendance, Please update your profile pic!'},202)

        data = request.data
        files = request.FILES
        if not data or not 'class' in data or not files or not 'avatar' in files:
            return Response({'success':False,'msg':'Data Required!'},202)

        classroom = Classroom.objects.filter(id=data.get('class'),students__in=[user]).first()
        if not classroom:
            return Response({'success':False,'msg':'Classroom does not exist!'},202)
        matched = match_face_template(files.get('avatar'),user.face_template)
        if not matched:
            return Response({'success':False,'msg':'Face not matched!'},202)

        today = date.today()
        attendance = classroom.attendances.filter(date=today).first()
        if not attendance:
            attendance = Attendance(classroom=classroom)
            attendance.save()

        attendance.students.add(user)
        return Response({'success':False,'msg':'Attendance marked!'},202)

class ListAttendance(ListAPIView, PaginationHandlerMixin):
    permission_classes = [IsAuthenticated, IsRoleTeacher]
    # pagination_class = Pagination
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        user = self.request.user
        current_date = timezone.now()
        seven_days_ago = current_date - timedelta(days=7)
        class_id = self.request.query_params.get('class_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if not class_id:
            return None
        
        queryset = Attendance.objects.filter(classroom_id=class_id, classroom__teacher=user).order_by('-date')

        if start_date and end_date:
            try:
                start_date_seconds = int(start_date) // 1000
                start_datetime = datetime.fromtimestamp(start_date_seconds)
                end_date_seconds = int(end_date) // 1000
                end_datetime = datetime.fromtimestamp(end_date_seconds)
                queryset = queryset.filter(created_on__gte=start_datetime, created_on__lte=end_datetime)
            except:
                return None
        else:
            queryset = queryset.filter(created_on__gte=seven_days_ago, created_on__lte=current_date)

        return queryset
        
