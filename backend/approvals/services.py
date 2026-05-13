"""
給其他 app 用的對外 API
其他 app 不要直接操作 ApprovalRequest / ApprovalStepRecord, 一律走 ApprovalService
"""
from django.db import transaction, models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from .models import (
    ApprovalFlow, ApprovalRequest, ApprovalStepRecord,
)
from .registry import get_resolver, get_condition


class ApprovalError(Exception):
    """審批操作失敗"""
    pass


class ApprovalService:

    # ============================================================
    # 內部: 解析某 step 在當前 context 下的可簽核 user_ids
    # ============================================================
    @staticmethod
    def _resolve_allowed_users(step, content_object, applicant) -> list[int]:
        """組合 靜態 user + 靜態 group 成員 + resolver 動態回傳, 回傳 user_id list"""
        ids: set[int] = set()

        # 1. 靜態指定 user
        if step.approver_user_id:
            ids.add(step.approver_user_id)

        # 2. 靜態指定 group → 群組內所有人
        if step.approver_group_id:
            group_user_ids = User.objects.filter(
                groups__id=step.approver_group_id
            ).values_list('id', flat=True)
            ids.update(group_user_ids)

        # 3. 動態 resolver
        if step.approver_resolver:
            fn = get_resolver(step.approver_resolver)
            if fn:
                result = fn(content_object=content_object, applicant=applicant)
                # 接受 User instance / list[User] / QuerySet / list[int]
                for item in result:
                    if isinstance(item, User):
                        ids.add(item.id)
                    elif isinstance(item, int):
                        ids.add(item)

        return list(ids)

    @staticmethod
    def _should_run_step(step, content_object, applicant) -> bool:
        """檢查 condition, 回傳 False 表示此關跳過"""
        if not step.condition_code:
            return True  # 沒設條件就一律執行
        fn = get_condition(step.condition_code)
        if fn is None:
            # condition_code 寫了但找不到 function, 保守起見執行
            return True
        return bool(fn(content_object=content_object, applicant=applicant))

    # ============================================================
    # 發起
    # ============================================================
    @staticmethod
    @transaction.atomic
    def start(content_object, flow_code: str, applicant: User, title: str = '') -> ApprovalRequest:
        try:
            flow = ApprovalFlow.objects.get(code=flow_code, is_active=True)
        except ApprovalFlow.DoesNotExist:
            raise ApprovalError(f'Flow not found: {flow_code}')

        steps = list(flow.steps.order_by('step_order'))
        if not steps:
            raise ApprovalError(f'Flow {flow_code} has no steps')

        request = ApprovalRequest.objects.create(
            flow=flow,
            content_type=ContentType.objects.get_for_model(content_object),
            object_id=content_object.pk,
            applicant=applicant,
            title=title or str(content_object),
            status='pending',
            current_step=steps[0].step_order,
        )

        first_active_order = None  # 第一個會跑的關卡

        for step in steps:
            should_run = ApprovalService._should_run_step(step, content_object, applicant)
            allowed = (
                ApprovalService._resolve_allowed_users(step, content_object, applicant)
                if should_run else []
            )

            record = ApprovalStepRecord.objects.create(
                request=request,
                step_order=step.step_order,
                step_name=step.name,
                expected_user=step.approver_user,
                expected_group=step.approver_group,
                allowed_user_ids=allowed,
                action='pending' if should_run else 'skipped',
                acted_at=timezone.now() if not should_run else None,
            )

            if should_run and first_active_order is None:
                first_active_order = step.step_order

        # 沒有任何要跑的關卡 → 直接通過 (邊界情況)
        if first_active_order is None:
            request.status = 'approved'
            request.completed_at = timezone.now()
            request.save()
        else:
            request.current_step = first_active_order
            request.save()

        return request

    # ============================================================
    # 簽核動作
    # ============================================================
    @staticmethod
    @transaction.atomic
    def approve(record_id: int, user: User, comment: str = '') -> ApprovalRequest:
        return ApprovalService._act(record_id, user, 'approved', comment)

    @staticmethod
    @transaction.atomic
    def reject(record_id: int, user: User, comment: str = '') -> ApprovalRequest:
        return ApprovalService._act(record_id, user, 'rejected', comment)

    @staticmethod
    def _act(record_id: int, user: User, action: str, comment: str) -> ApprovalRequest:
        try:
            record = ApprovalStepRecord.objects.select_related('request').get(pk=record_id)
        except ApprovalStepRecord.DoesNotExist:
            raise ApprovalError(f'Record {record_id} not found')

        req = record.request

        if record.action != 'pending':
            raise ApprovalError('This record has already been processed')
        if req.status != 'pending':
            raise ApprovalError(f'Request is already {req.status}')
        if record.step_order != req.current_step:
            raise ApprovalError('Not the current step')
        if user.id not in (record.allowed_user_ids or []):
            raise ApprovalError('You are not authorized to approve this step')

        record.actor = user
        record.action = action
        record.comment = comment
        record.acted_at = timezone.now()
        record.save()

        if action == 'rejected':
            req.status = 'rejected'
            req.completed_at = timezone.now()
            req.save()
            ApprovalStepRecord.objects.filter(
                request=req, action='pending',
            ).update(action='skipped', acted_at=timezone.now())
            return req

        # action == 'approved': 找下一關 (action 還是 pending 的)
        next_record = (
            ApprovalStepRecord.objects.filter(request=req, action='pending')
            .order_by('step_order').first()
        )
        if next_record is None:
            req.status = 'approved'
            req.completed_at = timezone.now()
            req.save()
        else:
            req.current_step = next_record.step_order
            req.save()
        return req

    # ============================================================
    # 撤回
    # ============================================================
    @staticmethod
    @transaction.atomic
    def cancel(request_id: int, user: User) -> ApprovalRequest:
        try:
            req = ApprovalRequest.objects.get(pk=request_id)
        except ApprovalRequest.DoesNotExist:
            raise ApprovalError('Request not found')

        if req.applicant_id != user.id:
            raise ApprovalError('Only applicant can cancel')
        if req.status != 'pending':
            raise ApprovalError(f'Cannot cancel a {req.status} request')

        req.status = 'cancelled'
        req.completed_at = timezone.now()
        req.save()
        ApprovalStepRecord.objects.filter(
            request=req, action='pending',
        ).update(action='skipped', acted_at=timezone.now())
        return req

    # ============================================================
    # Inbox: 我待簽的
    # ============================================================
    @staticmethod
    def get_inbox(user: User):
        """
        條件:
          - record action='pending'
          - 對應的 request status='pending'
          - record.step_order == request.current_step (當前關)
          - user.id 在 allowed_user_ids 內
        """
        return (
            ApprovalStepRecord.objects
            .select_related('request', 'request__flow', 'request__applicant')
            .filter(action='pending')
            .filter(request__status='pending')
            .filter(step_order=models.F('request__current_step'))
            # PostgreSQL JSONField __contains: 檢查 [user_id] 是否包含於 list 內
            .filter(allowed_user_ids__contains=[user.id])
            .order_by('-request__created_at')
        )

    # ============================================================
    # 自己發起的
    # ============================================================
    @staticmethod
    def get_my_requests(user: User, status: str = None):
        qs = (
            ApprovalRequest.objects
            .select_related('flow')
            .filter(applicant=user)
        )
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')
