"""
測試用 API: 發送訊息到 RabbitMQ
"""
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .producer import publish


class EHSMainTableDetailView(APIView):
    # JWT 認證 + 需登入
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        """
        POST body 範例:
        {
            "queue": "send_email",
            "payload": {"to": "a@b.com", "subject": "hi"}
        }
        """
        queue = request.data.get('queue')
        payload = request.data.get('payload', {})

        if not queue:
            return Response(
                {'error': 'queue is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            publish(queue, payload)
            return Response({'ok': True, 'queue': queue, 'payload': payload})
        except Exception as e:
            return Response(
                {'ok': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
