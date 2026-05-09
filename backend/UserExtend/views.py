"""
DRF ViewSets - 提供完整 CRUD API
"""
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import UserInfo, department
from .serializer import (
    UserSerializer, UserInfoSerializer, DepartmentSerializer,
)


# User ViewSet - 含註冊用的 create
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    # 搜尋與排序
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['id', 'username', 'date_joined']

    def get_permissions(self):
        # 註冊 (create) 開放, 其他要登入
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    # 取得目前登入者
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        ser = self.get_serializer(request.user)
        return Response(ser.data)


# Department ViewSet
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = department.objects.all().order_by('id')
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['id', 'name']


# UserInfo ViewSet
class UserInfoViewSet(viewsets.ModelViewSet):
    queryset = UserInfo.objects.select_related('user', 'department').all().order_by('id')
    serializer_class = UserInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'location', 'phone']
    ordering_fields = ['id', 'user__username']


# 登入: 回傳 token
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    # 取得或建立 token
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': {'id': user.id, 'username': user.username, 'email': user.email},
    })


# 登出: 刪除 token
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    Token.objects.filter(user=request.user).delete()
    return Response({'ok': True})
