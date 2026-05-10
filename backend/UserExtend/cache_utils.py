"""
Cache 工具 - 集中放 cache key 與常用 helper
寫 view 時直接 import 用即可
"""
from django.core.cache import cache


# ===== Cache key 集中管理 (避免散落各地) =====
class CacheKey:
    USER_DETAIL = 'user:detail:{user_id}'        # 單一使用者
    USER_LIST = 'user:list'                       # 使用者列表
    DEPARTMENT_LIST = 'department:list'           # 部門列表

    @staticmethod
    def format(template: str, **kwargs) -> str:
        return template.format(**kwargs)


# ===== 常用操作包裝 =====

def cache_get(key: str):
    """讀 cache, 沒有回 None"""
    return cache.get(key)


def cache_set(key: str, value, timeout: int = 300):
    """寫 cache, 預設 5 分鐘"""
    cache.set(key, value, timeout=timeout)


def cache_delete(key: str):
    """刪單一 key"""
    cache.delete(key)


def cache_delete_pattern(pattern: str):
    """
    刪符合 pattern 的所有 key (用 * 萬用字元)
    例: cache_delete_pattern('user:*')
    """
    cache.delete_pattern(pattern)


def get_or_set(key: str, callable_fn, timeout: int = 300):
    """
    有 cache 就回 cache, 沒有就跑 callable_fn() 並寫入
    用法: data = get_or_set('mykey', lambda: expensive_query())
    """
    value = cache.get(key)
    if value is None:
        value = callable_fn()
        cache.set(key, value, timeout=timeout)
    return value
