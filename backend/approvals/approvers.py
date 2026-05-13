"""
內建 resolver / condition
(各 app 也可以建立自己的 approvers.py, 啟動時會自動載入)
"""
from django.contrib.auth.models import User, Group
from .registry import register_resolver, register_condition


# ============================================================
# 內建 resolver: 動態決定簽核者
# ============================================================

@register_resolver('superusers')
def resolver_superusers(content_object, applicant):
    """所有 superuser 都可簽"""
    return User.objects.filter(is_superuser=True)


@register_resolver('staff_users')
def resolver_staff_users(content_object, applicant):
    """所有 staff 都可簽"""
    return User.objects.filter(is_staff=True)


@register_resolver('applicant_self')
def resolver_applicant_self(content_object, applicant):
    """申請人自己簽 (測試用)"""
    return [applicant]


# 範例: 申請人的部門主管 (依 UserExtend.UserInfo.department.supervisor)
@register_resolver('applicant_supervisor')
def resolver_applicant_supervisor(content_object, applicant):
    """申請人所屬部門的主管"""
    try:
        # 避開硬性 import 循環: 動態 import UserExtend
        from UserExtend.models import UserInfo
        info = UserInfo.objects.select_related('department__supervisor').get(user=applicant)
        if info.department and info.department.supervisor:
            return [info.department.supervisor]
    except Exception:
        pass
    return []


# ============================================================
# 內建 condition: 條件式跳關
# ============================================================

@register_condition('always_true')
def cond_always_true(content_object, applicant):
    return True


@register_condition('always_false')
def cond_always_false(content_object, applicant):
    return False


# 範例: 申請人不是 superuser 才需要這關
@register_condition('not_superuser')
def cond_not_superuser(content_object, applicant):
    return not applicant.is_superuser
