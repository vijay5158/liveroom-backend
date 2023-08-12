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

from .models import Announcement, Classroom, Comment, Post, Attendance, Assignment, AssignmentSubmission
from .serializers import (AnnouncementSerializer, AllClassRoomSerializer,AssignmentSerializer, AssignmentSubmissionSerializer,
                          CommentSerializer, PostSerializer, ClassRoomSerializer, AttendanceSerializer, AssignmentStudentSerializer)
# @csrf_exempt
from datetime import date
from Accounts.face_detection import match_face_template
from .permissions import IsRoleStudent, IsRoleTeacher
from rest_framework.pagination import LimitOffsetPagination
from .pagination import PaginationHandlerMixin
from rest_framework.generics import ListAPIView
from django.utils import timezone
from datetime import timedelta, datetime
from Liveroom.utils.helper import file_allowed_file

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
            return Response({"success":False,"message":"You are not authorized!"},status=HTTP_406_NOT_ACCEPTABLE)
        serializer = AnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            announcement = serializer.create(request)
            channel_layer = channels.layers.get_channel_layer()
            slug = announcement.classroom.slug
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
            return Response({"success":False,"message":"You are not authorized!"},status=HTTP_400_BAD_REQUEST)
        return Response({"success":False,"message":"Error, Try again"},status=HTTP_400_BAD_REQUEST)


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
            error = {"massage": "Classroom is locked", "success": False}
            return Response(error, status=HTTP_406_NOT_ACCEPTABLE)

        if classroom.students.count() >= classroom.limit:
            error = {"massage": "Classroom is full!", "success": False}
            return Response(error, status=HTTP_406_NOT_ACCEPTABLE)

        serialized = AllClassRoomSerializer(
            classroom, data=request.data, partial=True)
        if serialized.is_valid():
            updated_data = AllClassRoomSerializer.partial_update(
                self, instance=classroom, validated_data=request.data)
            if updated_data.lock == True:
                error = {"massage": "Classroom is locked", "success": False}
                return Response(error, status=HTTP_406_NOT_ACCEPTABLE)
            return Response(serialized.data, status=status.HTTP_202_ACCEPTED)

    def create(self, request):
        if request.user.is_student:
            return Response({"message":"You are not authorized", "success": False},status=HTTP_406_NOT_ACCEPTABLE)
        serializer = AllClassRoomSerializer(data=request.data)
        if serializer.is_valid():
            try:
                classroom = serializer.create(request)
                if classroom:
                    serialised_data = AllClassRoomSerializer(classroom)
                    return Response(serialised_data.data, status=HTTP_201_CREATED)
            except:
                return Response({"success":False, "message":"Error in class creation, Try again!"}, status=status.HTTP_400_BAD_REQUEST)        

        return Response(status=HTTP_400_BAD_REQUEST)

    def list(self, request):
        
        
        if request.user and request.user.is_teacher:
            classes = Classroom.objects.filter(teacher=request.user).order_by("-created_at")
        else:
            classes = Classroom.objects.filter(students=request.user).order_by("-created_at")

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
            if not data or not text or not classId:
                return Response({"message":"Data required!"},status=HTTP_400_BAD_REQUEST)
            classroom = Classroom.objects.get(id=classId,teacher=request.user)
            channel_layer = channels.layers.get_channel_layer()
            slug = classroom.slug
            file = files.get('file',None)
            if file and file_name:
                if file.name=="" or file_name=="" or not file_allowed_file(file.name):
                    return Response({"success":False, "message":"Allowed file type is 'pdf', 'docx', 'xlsx','mp3', 'mkv', 'mp4', 'ppt','pptx', 'odp', 'doc', 'png', 'jpeg', 'jpg'"},status=status.HTTP_400_BAD_REQUEST)
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
            return Response({"success":False, "message":"Class doesn't exists!"}, status=status.HTTP_400_BAD_REQUEST)

        # return Response(status=HTTP_400_BAD_REQUEST)
    # @xframe_options_exempt

    def list(self, request):
        # queryset = Post.objects.().order_by('-created_at')

        slug = request.query_params.get('slug')
        if slug is not None:
            queryset = Post.objects.filter(classroom__slug=slug).order_by('-created_at')
            if request.user.is_teacher:
                queryset = queryset.filter(classroom__teacher=request.user)
            else:
                queryset = queryset.filter(classroom__students=request.user)                
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            
            # Serialize the paginated queryset
            serializer = self.get_serializer(paginated_queryset, context={"request": request}, many=True)
            post_data = serializer.data
            posts_dict = {post['id']: post for post in post_data}
            # print(paginator.get_paginated_response(posts_dict))
            return paginator.get_paginated_response(posts_dict)

            # serializer = PostSerializer(
            #     queryset, context={"request": request}, many=True)
            
            # return Response(serializer.data)
        
        return Response({"success":False, "message":"Class id required!"}, status=status.HTTP_400_BAD_REQUEST)


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
            user = request.user
            classroom = Classroom.objects.filter(slug=slug).filter(Q(students=user) | Q(teacher=user)).first()
            if classroom:
                queryset = queryset.filter(post__classroom=classroom)
                serializer = CommentSerializer(queryset, many=True)
                return Response(serializer.data)
            return Response({"success":False, "message":"Class room doesn't exists!"}, status=status.HTTP_400_BAD_REQUEST)        

        return Response({"success":False, "message":"Class id required!"}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
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
        except:
            return Response({"success":False, "message":"Error Occured!"}, status=status.HTTP_400_BAD_REQUEST)        


class AttendanceAPIView(APIView):
    permission_classes=[IsAuthenticated, IsRoleStudent]

    def post(self,request):
        try:
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
            return Response({'success':True,'msg':'Attendance marked!'},202)
        except:
            return Response({"success":False, "message":"Error Occured!"}, status=status.HTTP_400_BAD_REQUEST)        

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
        
class CreateAssignmentAPIView(APIView):
    permission_classes=[IsAuthenticated, IsRoleTeacher]
    
    def post(self, request, slug):
        try:
            user = request.user
            if user.is_student:
                return Response({'success':False,'msg':'You are not authorized'},202)

            files = request.FILES
            data = request.data
            assignment_text = data.get("assignment_text",None)
            title = data.get("title",None)
            file = files.get("file", None)
            end_date = data.get("end_date",None)
            if not data or not assignment_text or not end_date or not title:
                return Response({"success":False, "message":"Assignment title, description and deadline is required!"}, status=status.HTTP_400_BAD_REQUEST)        
            if file and (file.name=="" or not file_allowed_file(file.name)):
                return Response({"success":False, "message":"Allowed file type is 'pdf', 'docx', 'xlsx','mp3', 'mkv', 'mp4', 'ppt','pptx', 'odp', 'doc', 'png', 'jpeg', 'jpg'"},status=status.HTTP_400_BAD_REQUEST)

            classroom_query = Classroom.objects.filter(slug=slug, teacher=request.user)
            if classroom_query.exists():
                classroom = classroom_query.first()
                assignment = Assignment.objects.create(title=title, assignment=assignment_text, created_by=request.user, classroom=classroom, file=file, end_date=end_date)
                serializer = AssignmentSerializer(assignment, context={"request": request})
                
                channel_layer = channels.layers.get_channel_layer()
                if serializer and slug:
                    async_to_sync(channel_layer.group_send)(
                        'class_'+slug,
                        {
                            'type': 'assignment_message',
                            'assignment': serializer.data
                        }
                    )

                return Response({"data":serializer.data, "success": True}, status=status.HTTP_201_CREATED)
            return Response({"success":False, "message":"Classroom doesn't exist!"}, status=status.HTTP_400_BAD_REQUEST)        

        except:
            return Response({"success":False, "message":"Error Occured!"}, status=status.HTTP_400_BAD_REQUEST)        

class GetAssignmentAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, slug):
        try:
            classroom_query = Classroom.objects.filter(slug=slug).filter(Q(teacher=request.user) | Q(students=request.user))
            if classroom_query.exists():
                classroom = classroom_query.first()
                assignments = classroom.assignments.order_by("-created_at").all()
                # if assignments:
                serializer = AssignmentStudentSerializer(assignments, context={"request": request}, many=True)
                return Response({"data":serializer.data, "success": True}, status=status.HTTP_200_OK)
                # return Response({"message":"Assignments not found!", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"success":False, "message":"Classroom doesn't exist!"}, status=status.HTTP_400_BAD_REQUEST)        

        except:
            return Response({"success":False, "message":"Error Occured!"}, status=status.HTTP_400_BAD_REQUEST)        

# class GetAssignmentStudentAPIView(APIView):
#     permission_classes=[IsAuthenticated, IsRoleStudent]

#     def get(self, request, slug):
#         try:
#             classroom_query = Classroom.objects.filter(slug=slug, students=request.user)
#             if classroom_query.exists():
#                 classroom = classroom_query.first()
#                 assignments = classroom.assignments.order_by("-created_at").all()
#                 if assignments:
#                     serializer = AssignmentStudentSerializer(assignments, context={"request": request}, many=True)
#                     return Response({"data":serializer.data, "success": True}, status=status.HTTP_200_OK)
#                 return Response({"message":"Assignments not found!", "success": False}, status=status.HTTP_400_BAD_REQUEST)
#             return Response({"success":False, "message":"Classroom doesn't exist!"}, status=status.HTTP_400_BAD_REQUEST)        

#         except:
#             return Response({"success":False, "message":"Error Occured!"}, status=status.HTTP_400_BAD_REQUEST)        


class CreateAssignmentSubmissionAPIView(APIView):
    permission_classes=[IsAuthenticated, IsRoleStudent]
    
    def post(self, request, slug):
        try:
            data = request.data
            assignment_id = data.get("assignment_id",None)
            user = request.user
            if user.is_teacher:
                return Response({'success':False,'msg':'You are not authorized'},202)

            files = request.FILES
            file = files.get("file", None)
            if not file or not assignment_id:
                return Response({"success":False, "message":"Assignment file required!"}, status=status.HTTP_400_BAD_REQUEST)        
            if file.name=="" or not file_allowed_file(file.name):
                return Response({"success":False, "message":"Allowed file type is 'pdf', 'docx', 'xlsx','mp3', 'mkv', 'mp4', 'ppt','pptx', 'odp', 'doc', 'png', 'jpeg', 'jpg'"},status=status.HTTP_400_BAD_REQUEST)

            classroom_query = Classroom.objects.filter(slug=slug, students=request.user)
            if classroom_query.exists():
                classroom = classroom_query.first()
                try:
                    assignment = Assignment.objects.get(id=assignment_id, classroom=classroom)
                    if assignment.end_date is not None and assignment.end_date <= timezone.now():
                        return Response({"success":False, "message":"Assignment deadline gone!"}, status=status.HTTP_400_BAD_REQUEST)        
                    assignment_sub, created = AssignmentSubmission.objects.get_or_create(created_by=request.user, assignment=assignment, defaults={file: file})
                    serializer = AssignmentSubmissionSerializer(assignment_sub, context={"request": request})
                    if not created:
                        return Response({"success":True, "data":serializer.data, "message":"Assignment already submitted!"}, status=status.HTTP_200_OK)        
                    return Response({"success":True, "data":serializer.data, "message":"Assignment submitted!"}, status=status.HTTP_201_CREATED)        
                    
                except:
                    return Response({"success":False, "message":"Assignment doesn't exist!"}, status=status.HTTP_400_BAD_REQUEST)        
            return Response({"success":False, "message":"Classroom doesn't exist!"}, status=status.HTTP_400_BAD_REQUEST)        

        except:
            return Response({"success":False, "message":"Error Occured!"}, status=status.HTTP_400_BAD_REQUEST)        


class AssignmentSubmissionAPIView(APIView):
    permission_classes=[IsAuthenticated, IsRoleTeacher]
    
    def post(self, request, slug):
        try:
            data = request.data
            assignment_id = data.get("assignment_id",None)
            user = request.user
            if user.is_student:
                return Response({'success':False,'msg':'You are not authorized'},202)

            if not assignment_id:
                return Response({"success":False, "message":"Data required!"}, status=status.HTTP_400_BAD_REQUEST)        

            classroom_query = Classroom.objects.filter(slug=slug, teacher=request.user)
            if classroom_query.exists():
                classroom = classroom_query.first()
                try:
                    assignment = Assignment.objects.get(id=assignment_id, classroom=classroom)
                    assignment_subs = AssignmentSubmission.objects.filter(assignment=assignment).order_by("created_at")
                    serializer = AssignmentSubmissionSerializer(assignment_subs, context={"request": request}, many=True)
                    return Response({"success":True, "data":serializer.data}, status=status.HTTP_201_CREATED)        
                    
                except:
                    return Response({"success":False, "message":"Assignment doesn't exist!"}, status=status.HTTP_400_BAD_REQUEST)        
            return Response({"success":False, "message":"Classroom doesn't exist!"}, status=status.HTTP_400_BAD_REQUEST)        

        except:
            return Response({"success":False, "message":"Error Occured!"}, status=status.HTTP_400_BAD_REQUEST)        


class CheckAssignmentSubmissionAPIView(APIView):
    permission_classes=[IsAuthenticated, IsRoleTeacher]
    
    def post(self, request, slug):
        try:
            data = request.data
            assignment_id = data.get("assignment_id",None)
            submission_id = data.get("submission_id",None)
            score = data.get("score",None)
            remarks = data.get("remarks",None)
            user = request.user
            if user.is_student:
                return Response({'success':False,'msg':'You are not authorized'},202)

            if not submission_id or not assignment_id or not score:
                return Response({"success":False, "message":"Data required!"}, status=status.HTTP_400_BAD_REQUEST)        

            classroom_query = Classroom.objects.filter(slug=slug, teacher=request.user)
            if classroom_query.exists():
                classroom = classroom_query.first()
                try:
                    assignment = Assignment.objects.get(id=assignment_id, classroom=classroom)
                    assignment_sub = AssignmentSubmission.objects.get(id=submission_id, assignment=assignment)
                    assignment_sub.score = score
                    assignment_sub.remarks = remarks
                    assignment_sub.save()
                    serializer = AssignmentSubmissionSerializer(assignment_sub, context={"request": request})
                    return Response({"success":True, "data":serializer.data, "message":"Submission updated!"}, status=status.HTTP_201_CREATED)        
                    
                except:
                    return Response({"success":False, "message":"Assignment doesn't exist!"}, status=status.HTTP_400_BAD_REQUEST)        
            return Response({"success":False, "message":"Classroom doesn't exist!"}, status=status.HTTP_400_BAD_REQUEST)        

        except:
            return Response({"success":False, "message":"Error Occured!"}, status=status.HTTP_400_BAD_REQUEST)        
