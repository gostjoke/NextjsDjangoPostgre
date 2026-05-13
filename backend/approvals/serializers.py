"""
Approval API serializers
"""
from rest_framework import serializers
from .models import (
    ApprovalFlow, ApprovalFlowStep,
    ApprovalRequest, ApprovalStepRecord,
)


class ApprovalFlowStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalFlowStep
        fields = ['id', 'step_order', 'name', 'approver_user', 'approver_group', 'is_required']


class ApprovalFlowSerializer(serializers.ModelSerializer):
    steps = ApprovalFlowStepSerializer(many=True, read_only=True)

    class Meta:
        model = ApprovalFlow
        fields = ['id', 'code', 'name', 'description', 'is_active', 'steps']


class ApprovalStepRecordSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    expected_user_name = serializers.CharField(source='expected_user.username', read_only=True)
    expected_group_name = serializers.CharField(source='expected_group.name', read_only=True)

    class Meta:
        model = ApprovalStepRecord
        fields = [
            'id', 'step_order', 'step_name',
            'expected_user', 'expected_user_name',
            'expected_group', 'expected_group_name',
            'actor', 'actor_name',
            'action', 'comment',
            'created_at', 'acted_at',
        ]


class ApprovalRequestSerializer(serializers.ModelSerializer):
    flow_code = serializers.CharField(source='flow.code', read_only=True)
    flow_name = serializers.CharField(source='flow.name', read_only=True)
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    records = ApprovalStepRecordSerializer(many=True, read_only=True)
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = ApprovalRequest
        fields = [
            'id', 'flow', 'flow_code', 'flow_name',
            'content_type', 'content_type_name', 'object_id',
            'applicant', 'applicant_name', 'title',
            'status', 'current_step',
            'created_at', 'updated_at', 'completed_at',
            'records',
        ]


# Inbox 用簡化版 (列表顯示, 不展開全部 records)
class InboxRecordSerializer(serializers.ModelSerializer):
    request_id = serializers.IntegerField(source='request.id', read_only=True)
    flow_code = serializers.CharField(source='request.flow.code', read_only=True)
    flow_name = serializers.CharField(source='request.flow.name', read_only=True)
    title = serializers.CharField(source='request.title', read_only=True)
    applicant_name = serializers.CharField(source='request.applicant.username', read_only=True)
    created_at = serializers.DateTimeField(source='request.created_at', read_only=True)

    class Meta:
        model = ApprovalStepRecord
        fields = [
            'id',  # record id (簽核用)
            'request_id',
            'flow_code', 'flow_name',
            'title', 'applicant_name',
            'step_order', 'step_name',
            'created_at',
        ]


# 簽核動作的 input
class ActionSerializer(serializers.Serializer):
    comment = serializers.CharField(allow_blank=True, required=False, default='')
