"""
Approval API
"""
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import ApprovalFlow, ApprovalRequest
from .services import ApprovalService, ApprovalError
from .serializers import (
    ApprovalFlowSerializer,
    ApprovalRequestSerializer,
    InboxRecordSerializer,
    ActionSerializer,
)


# 流程定義 (只讀)
class ApprovalFlowViewSet(ReadOnlyModelViewSet):
    queryset = ApprovalFlow.objects.filter(is_active=True).prefetch_related('steps')
    serializer_class = ApprovalFlowSerializer
    permission_classes = [IsAuthenticated]


# 單據查詢 (只讀, 寫入要走 service)
class ApprovalRequestViewSet(ReadOnlyModelViewSet):
    queryset = ApprovalRequest.objects.select_related('flow', 'applicant').prefetch_related('records')
    serializer_class = ApprovalRequestSerializer
    permission_classes = [IsAuthenticated]


# Inbox: 我待簽的
class InboxView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = ApprovalService.get_inbox(request.user)
        ser = InboxRecordSerializer(records, many=True)
        return Response({'count': len(ser.data), 'results': ser.data})


# 我發起的
class MyRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_filter = request.query_params.get('status')
        qs = ApprovalService.get_my_requests(request.user, status=status_filter)
        ser = ApprovalRequestSerializer(qs, many=True)
        return Response({'count': len(ser.data), 'results': ser.data})


# 通過某一關
class ApproveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, record_id):
        ser = ActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            req = ApprovalService.approve(
                record_id=record_id,
                user=request.user,
                comment=ser.validated_data.get('comment', ''),
            )
            return Response(ApprovalRequestSerializer(req).data)
        except ApprovalError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 退回某一關
class RejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, record_id):
        ser = ActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            req = ApprovalService.reject(
                record_id=record_id,
                user=request.user,
                comment=ser.validated_data.get('comment', ''),
            )
            return Response(ApprovalRequestSerializer(req).data)
        except ApprovalError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 撤回單據 (發起人)
class CancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        try:
            req = ApprovalService.cancel(request_id=request_id, user=request.user)
            return Response(ApprovalRequestSerializer(req).data)
        except ApprovalError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
