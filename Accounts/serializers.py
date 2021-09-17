from rest_auth.serializers import LoginSerializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import Contact, CustomUser


class loginSerializer(LoginSerializer):
    username = None

class RegistrationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=400, read_only=True)
    is_student = serializers.BooleanField()
    is_teacher = serializers.BooleanField()
    class Meta:
        model = CustomUser
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            
            instance.set_password(password)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        
        model = CustomUser
        fields = '__all__'

    def update(self, instance, validated_data):
        if validated_data.get('password') is not None:
            password = validated_data.pop('password', None)
            if password is not None:
                instance.set_password(password)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.profile_img = validated_data.get('profile_img', instance.profile_img)
        instance.save()
        return instance

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class TokenSerializer(serializers.ModelSerializer):
    user_data = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = ('key', 'user', 'user_data')


    def get_user_data(self, obj):

        profile_img = serializers.ImageField(max_length=None, use_url=True)

        serializer_data = UserSerializer(obj.user).data
        first_name = serializer_data.get('first_name')
        last_name = serializer_data.get('last_name')
        mobile = serializer_data.get('mobile')
        profile_img = serializer_data.get('profile_img')
        is_student = serializer_data.get('is_student')
        is_teacher = serializer_data.get('is_teacher')
        return {
            'first_name': first_name,
            'last_name': last_name,
            'mobile': mobile,
            'profile_img':profile_img,
            'is_student': is_student,
            'is_teacher': is_teacher
        }
