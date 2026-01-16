from rest_framework import serializers
from models import UserInfo

class UserInfoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserInfo
        fields = ['username', 'email', 'bio', 'location', 'birth_date', 'phone', 'address']
