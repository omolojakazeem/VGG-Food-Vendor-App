from rest_framework import serializers
from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','user_type',]


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

        read_only_fields = [
                    'is_superuser',
                    'groups',
                    'user_permissions',
                    'password',
                    'username',
                    'is_staff',
                    'is_active',
                ]


class UserVerifySerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(allow_blank=False, write_only=True)

    class Meta:
        model = User
        fields = ['password','confirm_password',]


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','password']
