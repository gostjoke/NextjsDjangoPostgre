from django.apps import AppConfig


class ApprovalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'approvals'
    verbose_name = 'Approval Workflow'

    def ready(self):
        # 自動掃描所有 installed app 的 approvers.py
        # 讓各 app 能用 @register_resolver / @register_condition 註冊自訂邏輯
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('approvers')
