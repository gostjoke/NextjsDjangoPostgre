"""
通用審批流程
設計概念:
  ApprovalFlow         -> 流程定義 (template), 例如「請假流程」
  ApprovalFlowStep     -> 流程的各關卡, 例如 第1關主管 / 第2關HR
  ApprovalRequest      -> 實際發起的一筆審批 (掛到任何 model 上, 用 GenericFK)
  ApprovalStepRecord   -> 每一關的簽核紀錄 (底表 / audit log)

其他 app 怎麼用:
  from approvals.services import ApprovalService
  req = ApprovalService.start(my_obj, flow_code='leave', applicant=user)
"""
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# ============================================================
# 流程定義
# ============================================================

class ApprovalFlow(models.Model):
    """流程模板 (例如 leave_request, expense_claim, purchase_order)"""
    code = models.CharField(
        max_length=50, unique=True,
        help_text='程式內使用的 key, e.g. "leave_request"',
    )
    name = models.CharField(max_length=100, help_text='顯示名稱')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Approval Flow'
        verbose_name_plural = 'Approval Flows'

    def __str__(self):
        return f'[{self.code}] {self.name}'


class ApprovalFlowStep(models.Model):
    """流程的每一個關卡 (依 order 順序執行)"""
    flow = models.ForeignKey(
        ApprovalFlow, on_delete=models.CASCADE, related_name='steps',
    )
    step_order = models.PositiveIntegerField(help_text='第幾關 (1, 2, 3...)')
    name = models.CharField(max_length=100, help_text='關卡名稱, 例如「主管簽核」')
    # 指定簽核人: user 或 group 二擇一 (或都填, 兩邊都可簽)
    approver_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='+', help_text='指定特定使用者 (靜態, 可選)',
    )
    approver_group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='+', help_text='指定群組 (靜態, 可選)',
    )
    # 動態決定簽核者 (從 registry 取對應 function 執行)
    approver_resolver = models.CharField(
        max_length=100, blank=True,
        help_text='resolver code, 動態算出可簽核者 (例如 applicant_manager)',
    )
    # 條件判斷: 回傳 False 此關直接 skipped
    condition_code = models.CharField(
        max_length=100, blank=True,
        help_text='condition code, 不滿足條件時跳過此關 (例如 high_amount)',
    )
    is_required = models.BooleanField(default=True, help_text='是否必經此關')

    class Meta:
        verbose_name = 'Approval Step'
        verbose_name_plural = 'Approval Steps'
        ordering = ['flow', 'step_order']
        unique_together = [('flow', 'step_order')]

    def __str__(self):
        return f'{self.flow.code} #{self.step_order} {self.name}'


# ============================================================
# 實際單據
# ============================================================

class ApprovalRequest(models.Model):
    """審批單據 (掛到任何 model 上)"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),         # 簽核中
        ('approved', 'Approved'),       # 完全通過
        ('rejected', 'Rejected'),       # 被退回
        ('cancelled', 'Cancelled'),     # 發起人撤回
    ]

    flow = models.ForeignKey(
        ApprovalFlow, on_delete=models.PROTECT, related_name='requests',
    )
    # GenericFK: 可掛任何 model (例如 LeaveRequest, Order, PurchaseRequest...)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    applicant = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='approval_requests',
        help_text='發起人',
    )
    title = models.CharField(
        max_length=200, blank=True,
        help_text='單據標題, 在 inbox 顯示用',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending',
    )
    current_step = models.PositiveIntegerField(
        default=1, help_text='目前進行到第幾關',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Approval Request'
        verbose_name_plural = 'Approval Requests'
        ordering = ['-created_at']
        indexes = [
            # inbox 用: 依 status / step 查
            models.Index(fields=['status', 'current_step']),
            models.Index(fields=['applicant', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f'[{self.flow.code}#{self.id}] {self.title or self.content_object}'


class ApprovalStepRecord(models.Model):
    """每一關的簽核紀錄 (底表, 全部保留, 不刪除)"""
    ACTION_CHOICES = [
        ('pending', 'Pending'),     # 待簽
        ('approved', 'Approved'),   # 通過
        ('rejected', 'Rejected'),   # 退回
        ('skipped', 'Skipped'),     # 跳過
    ]

    request = models.ForeignKey(
        ApprovalRequest, on_delete=models.CASCADE, related_name='records',
    )
    # snapshot 步驟資訊 (即使 step 設定改了, 紀錄不變)
    step_order = models.PositiveIntegerField()
    step_name = models.CharField(max_length=100)
    # 預期簽核者 (可能是 user 或 group)
    expected_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='+',
    )
    expected_group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='+',
    )
    # 實際簽核者 (簽完才有)
    actor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approval_records',
    )
    # snapshot: 啟動單據時解析出來的可簽核 user ids
    # (含 resolver 動態算出的 + 靜態指定 user). 比 M2M 簡單, 也保留歷史
    allowed_user_ids = models.JSONField(
        default=list, blank=True,
        help_text='[user_id, ...] 此關可簽核的 user id 列表 (snapshot)',
    )
    action = models.CharField(
        max_length=20, choices=ACTION_CHOICES, default='pending',
    )
    comment = models.TextField(blank=True, help_text='簽核意見')

    created_at = models.DateTimeField(auto_now_add=True)
    acted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Approval Record'
        verbose_name_plural = 'Approval Records'
        ordering = ['request', 'step_order']
        indexes = [
            # inbox 查詢用: 找某人待簽的
            models.Index(fields=['action', 'expected_user']),
            models.Index(fields=['action', 'expected_group']),
            models.Index(fields=['request', 'step_order']),
        ]

    def __str__(self):
        return f'Req#{self.request_id} step{self.step_order} {self.action}'
