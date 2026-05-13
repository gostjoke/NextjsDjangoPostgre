"""
Approval admin
"""
from django.contrib import admin
from .models import (
    ApprovalFlow, ApprovalFlowStep,
    ApprovalRequest, ApprovalStepRecord,
)


class ApprovalFlowStepInline(admin.TabularInline):
    model = ApprovalFlowStep
    extra = 1


@admin.register(ApprovalFlow)
class ApprovalFlowAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')
    inlines = [ApprovalFlowStepInline]


class ApprovalStepRecordInline(admin.TabularInline):
    model = ApprovalStepRecord
    extra = 0
    readonly_fields = (
        'step_order', 'step_name',
        'expected_user', 'expected_group',
        'allowed_user_ids',
        'actor', 'action', 'comment',
        'created_at', 'acted_at',
    )
    can_delete = False


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'flow', 'title', 'applicant', 'status', 'current_step', 'created_at',
    )
    list_filter = ('status', 'flow')
    search_fields = ('title', 'applicant__username')
    readonly_fields = (
        'flow', 'content_type', 'object_id',
        'applicant', 'created_at', 'updated_at', 'completed_at',
    )
    inlines = [ApprovalStepRecordInline]


@admin.register(ApprovalStepRecord)
class ApprovalStepRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'request', 'step_order', 'step_name',
        'expected_user', 'actor', 'action', 'acted_at',
    )
    list_filter = ('action',)
    search_fields = ('step_name', 'comment')
    readonly_fields = (
        'request', 'step_order', 'step_name',
        'expected_user', 'expected_group',
        'allowed_user_ids',
        'created_at',
    )
