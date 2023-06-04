from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import Contact, CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    is_student = serializers.BooleanField()
    is_teacher = serializers.BooleanField()
    class Meta:
        model = CustomUser
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('user_permissions',None)
        validated_data.pop('groups',None)
        validated_data.pop('is_active',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        
        model = CustomUser
        fields = ('name','email','mobile','profile_img','is_student','is_teacher','id', )

    def update(self, instance, validated_data):
        if validated_data.get('password') is not None:
            password = validated_data.pop('password', None)
            if password is not None:
                instance.set_password(password)
        instance.name = validated_data.get('name', instance.name)
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
        name = serializer_data.get('name')
        mobile = serializer_data.get('mobile')
        profile_img = serializer_data.get('profile_img')
        is_student = serializer_data.get('is_student')
        is_teacher = serializer_data.get('is_teacher')
        return {
            'name': name,
            'mobile': mobile,
            'profile_img':profile_img,
            'is_student': is_student,
            'is_teacher': is_teacher
        }
