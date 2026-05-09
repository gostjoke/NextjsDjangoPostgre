"""
DRF Serializers
"""
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserInfo, department


# User serializer - 給註冊用 (含 password write_only)
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        # 建 user 時要用 create_user 才會 hash password
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# 簡化版 user 顯示用 (給巢狀 read 用)
class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


# Department serializer
class DepartmentSerializer(serializers.ModelSerializer):
    # read 時顯示 supervisor 詳細, write 時用 id
    supervisor_detail = UserBriefSerializer(source='supervisor', read_only=True)

    class Meta:
        model = department
        fields = ['id', 'name', 'description', 'supervisor', 'supervisor_detail']


# UserInfo serializer - 含 nested user / department
class UserInfoSerializer(serializers.ModelSerializer):
    user_detail = UserBriefSerializer(source='user', read_only=True)
    department_detail = DepartmentSerializer(source='department', read_only=True)

    class Meta:
        model = UserInfo
        fields = [
            'id', 'user', 'user_detail',
            'bio', 'location', 'birth_date', 'phone', 'address',
            'department', 'department_detail',
        ]
