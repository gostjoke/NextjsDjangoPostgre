from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from mq.producer import publish


class TestView(APIView):
    # 開放給匿名訪問 (測試/壓測用)
    permission_classes = [AllowAny]
    authentication_classes = []  # 完全不做認證, 加快壓測

    def get(self, request):
        publish('send_email', {
            'to': "test",
            'subject': '歡迎加入',
            'body': f'Hi ',
        })
        return Response({'message': 'hello'}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data  # DRF 的 request，自動解析 JSON

        if not data.get('name'):
            return Response(
                {'error': '名稱不能為空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'id': 1, 'name': data['name']},
            status=status.HTTP_201_CREATED
        )
