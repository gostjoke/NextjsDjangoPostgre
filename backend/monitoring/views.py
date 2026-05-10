"""
QPS 查詢 API
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .middleware import get_qps_stats


class QPSView(APIView):
    # 監控端點開放給內網 (生產環境記得加 IP 白名單)
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        # ?window=30  自訂時間窗 (秒)
        window = int(request.query_params.get('window', 10))
        window = min(max(window, 1), 60)  # 限制 1~60 秒
        stats = get_qps_stats(window_seconds=window)
        return Response(stats)
