from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import authenticate,login
from .tokens import create_jwt_pair_for_user
from .models import CustomUser
from .serializers import (ContactSerializer, RegistrationSerializer,
                          UserSerializer)
from .face_detection import get_face_template
from .helper import compress_and_resize, generate_unique_filename
from django.core.files.base import ContentFile
from Liveroom.utils.helper import avatar_allowed_file

class ContactView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format='json'):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            contact = serializer.save()
            if contact:
                json = serializer.data
                return Response(json,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)




class UserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    # queryset = CustomUser.objects.all()
    # serializer_class = UserSerializer

    def list(self,request):
        user = request.user
        if user:
            serialized = UserSerializer(user)
            return Response(serialized.data,status=status.HTTP_200_OK)

        return Response({"success":False},status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self,request,pk=None):
        user = request.user

        if user:
            files = request.FILES
            if 'avatar' in files:
                avatar = files.get('avatar')
                if avatar.name=="" or not avatar_allowed_file(avatar.name):
                    return Response({"success":False, "message":"Allowed avatar type is jpg, jpeg, png"},status=status.HTTP_400_BAD_REQUEST)
                try:
                    compressed_avatar = compress_and_resize(avatar)
                    newFile = ContentFile(compressed_avatar, name=generate_unique_filename(avatar.name))
                    user.profile_img = newFile
                    try:
                        face_template = get_face_template(newFile)
                        # print(face_template)
                        user.face_template = face_template
                    except Exception as e:
                        print('error',e)
                        pass
                    user.save()
                except:
                    pass
            
            serialized = UserSerializer(
            user, data=request.data, partial=True)
            if serialized.is_valid():
                updated_data = UserSerializer.update(
                self, instance=user, validated_data=request.data)
                return Response(serialized.data, status=status.HTTP_202_ACCEPTED)

        return Response({"success":False, "message":"Error, Try again!"},status=status.HTTP_400_BAD_REQUEST)



class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]


    def post(self, request, format='json'):
        data = request.data.copy()
        if data["is_student"]=='true' or data["is_student"]=='True':
            data["is_student"]=True            
            data["is_teacher"]=False
        elif data["is_teacher"]=='true' or data["is_teacher"]=='True':
            data["is_student"]=False            
            data["is_teacher"]=True
        serializer = RegistrationSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            # files = request.FILES
            # if 'avatar' in files:
            #     avatar = files.get('avatar')
            #     try:
            #         face_template = get_face_template(avatar)
            #         # print(face_template)
            #         user.face_template = face_template
            #         user.save()
            #     except Exception as e:
            #         print('error',e)
            #         pass

            if user:
                login(request,user)
                tokens = create_jwt_pair_for_user(user)
                # print(tokens)
                json = serializer.data
                # json["tokens"] = str(tokens)
                data = {
                    "user":json,
                    "tokens":tokens
                }
                return Response(data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request,user)
                serialized = UserSerializer(user)
                tokens = create_jwt_pair_for_user(user)
                response = {
                        "user":serialized.data,
                        "tokens":tokens,
                        "message": "Login Successfull",
                        "success":True
                }
                return Response(data=response, status=status.HTTP_200_OK)

            else:
                return Response(data={"message": "Invalid email or password","success":False})
        except:
            return Response(data={"message": "Something wrong happend!","success":False})
    def get(self, request: Request):
        content = {"user": str(request.user), "auth": str(request.auth)}

        return Response(data=content, status=status.HTTP_200_OK)
    
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)

        except Exception:
            return Response({'message': 'Invalid refresh token.'}, status=400)
