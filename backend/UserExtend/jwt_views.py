"""
自訂 JWT 登入 view - 回傳 token + 使用者資料
"""
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """擴充: 在 token payload 多塞一些 user 資料"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 把這些欄位放進 token payload (前端 decode 就拿得到)
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        return token

    def validate(self, attrs):
        # 預設只回 {access, refresh}, 我們多回 user 資料
        data = super().validate(attrs)
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        return data


class JWTLoginView(TokenObtainPairView):
    """
    POST /api/userextend/auth/jwt/login/
    body: { "username": "xxx", "password": "xxx" }
    回傳:
    {
        "access": "...",
        "refresh": "...",
        "user": { id, username, email, ... }
    }
    """
    serializer_class = CustomTokenObtainPairSerializer
