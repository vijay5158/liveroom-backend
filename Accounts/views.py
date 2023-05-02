from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from django.contrib.auth import authenticate,login
from .tokens import create_jwt_pair_for_user
from .models import CustomUser
from .serializers import (ContactSerializer, RegistrationSerializer,
                          UserSerializer)


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

        return Response({"error":True},status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self,request,pk=None):
        user = request.user

        if user:
            serialized = UserSerializer(
            user, data=request.data, partial=True)
            if serialized.is_valid():
                updated_data = UserSerializer.update(
                self, instance=user, validated_data=request.data)
                return Response(serialized.data, status=status.HTTP_202_ACCEPTED)

        return Response({"error":True},status=status.HTTP_400_BAD_REQUEST)



class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]


    def post(self, request, format='json'):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            if user:
                login(request,user)
                tokens = create_jwt_pair_for_user(user)
                print(tokens)
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