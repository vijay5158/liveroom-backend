from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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




class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer



class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]


    def post(self, request, format='json'):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json["token"] = str(token)
                return Response(json,status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


