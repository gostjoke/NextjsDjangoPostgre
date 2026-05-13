"""
Resolver / Condition 註冊中心

其他 app 用 decorator 註冊自訂的簽核者解析器 / 條件判斷:

# 在 OnlineStore/approvers.py
from approvals.registry import register_resolver, register_condition

@register_resolver('order_supervisor')
def get_order_supervisor(content_object, applicant):
    \"\"\"動態決定誰能簽核此單據, 回傳 User queryset 或 list\"\"\"
    return User.objects.filter(groups__name='Order Supervisor')

@register_condition('high_amount')
def is_high_amount(content_object, applicant):
    \"\"\"回傳 True 才需要這一關, False 直接跳過\"\"\"
    return content_object.total_amount > 100000

之後在 admin 建立 ApprovalFlowStep 時, approver_resolver 欄位填 'order_supervisor',
condition_code 填 'high_amount' 即可
"""
from typing import Callable

# 註冊表 (process 啟動時填充)
_RESOLVERS: dict[str, Callable] = {}
_CONDITIONS: dict[str, Callable] = {}


def register_resolver(code: str):
    """裝飾器: 註冊簽核者解析器"""
    def decorator(fn: Callable):
        _RESOLVERS[code] = fn
        return fn
    return decorator


def register_condition(code: str):
    """裝飾器: 註冊條件判斷"""
    def decorator(fn: Callable):
        _CONDITIONS[code] = fn
        return fn
    return decorator


def get_resolver(code: str) -> Callable | None:
    return _RESOLVERS.get(code)


def get_condition(code: str) -> Callable | None:
    return _CONDITIONS.get(code)


def list_resolvers() -> list[str]:
    return sorted(_RESOLVERS.keys())


def list_conditions() -> list[str]:
    return sorted(_CONDITIONS.keys())
