"""
Approval URL routes
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ApprovalFlowViewSet, ApprovalRequestViewSet,
    InboxView, MyRequestsView,
    ApproveView, RejectView, CancelView,
)

router = DefaultRouter()
router.register(r'flows', ApprovalFlowViewSet, basename='flow')
router.register(r'requests', ApprovalRequestViewSet, basename='request')

urlpatterns = [
    # CRUD via router
    path('', include(router.urls)),
    # Inbox: 我待簽的
    path('inbox/', InboxView.as_view(), name='approval-inbox'),
    # 我發起的
    path('mine/', MyRequestsView.as_view(), name='approval-mine'),
    # 動作
    path('records/<int:record_id>/approve/', ApproveView.as_view(), name='approval-approve'),
    path('records/<int:record_id>/reject/', RejectView.as_view(), name='approval-reject'),
    path('requests/<int:request_id>/cancel/', CancelView.as_view(), name='approval-cancel'),
]
