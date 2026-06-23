from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Member
from .serializers import MemberSerializer


class MemberViewSet(viewsets.ModelViewSet):
    """
    Member CRUD + 自訂登入
    - POST /members/          -> 註冊 (AllowAny)
    - POST /members/login/    -> 登入, 回傳 JWT
    - 其餘 CRUD 需 IsAuthenticated
    """
    queryset = Member.objects.all().order_by('id')
    serializer_class = MemberSerializer
    authentication_classes = [JWTAuthentication]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'name', 'phone']
    ordering_fields = ['id', 'created_at']

    def get_permissions(self):
        # 註冊 / 登入 不需驗證
        if self.action in ('create', 'login'):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """
        POST body: { "email": "...", "password": "..." }
        回傳: { "access": "...", "refresh": "...", "member": {...} }
        """
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'email and password required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            member = Member.objects.get(email=email, is_active=True)
        except Member.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not member.check_password(password):
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # 用 simplejwt RefreshToken 產生 token, 塞自訂 claim
        refresh = RefreshToken()
        refresh['member_id'] = member.id
        refresh['email'] = member.email
        refresh['token_type'] = 'member'  # 區分與 Django User token

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'member': MemberSerializer(member).data,
        })
