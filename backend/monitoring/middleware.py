"""
QPS 統計 middleware
用 Redis 以「每秒一個 key」的方式累計請求數, TTL 60 秒自動清掉舊資料
"""
import time
from django.core.cache import cache


class QPSMiddleware:
    """
    記錄每秒收到的 request 數量到 Redis
    Key 結構: qps:{epoch_second}
    每個 key TTL 60 秒, 自動過期
    """

    # Redis key prefix
    KEY_PREFIX = 'qps'
    # 保留多久的數據 (秒)
    KEEP_SECONDS = 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 用當前秒數當 key, 同一秒內的請求累加在同一個 key
        now_second = int(time.time())
        key = f'{self.KEY_PREFIX}:{now_second}'

        # 原子操作: incr + 設 TTL (用 Redis client 直接呼叫, 比 cache.incr 快)
        # 用 fire-and-forget: 設極短 timeout, Redis 卡就直接跳過
        try:
            from django_redis import get_redis_connection
            conn = get_redis_connection('default')
            # 設極短 socket timeout, 避免 middleware 拖慢請求
            conn.connection_pool.connection_kwargs['socket_timeout'] = 0.05  # 50ms
            full_key = f':backend:{key}'
            pipe = conn.pipeline()
            pipe.incr(full_key)
            pipe.expire(full_key, self.KEEP_SECONDS)
            pipe.execute()
        except Exception:
            # Redis 掛掉 / 超時都不影響正常請求
            pass

        # 繼續處理請求
        response = self.get_response(request)
        return response


def get_qps_stats(window_seconds: int = 10):
    """
    計算過去 N 秒的 QPS 統計
    回傳: {
        'window': 秒數,
        'total_requests': 總數,
        'avg_qps': 平均 QPS,
        'max_qps': 最高 QPS (秒級),
        'per_second': [{second: ts, count: n}, ...]
    }
    """
    try:
        from django_redis import get_redis_connection
        conn = get_redis_connection('default')

        now_second = int(time.time())
        keys = [f':backend:qps:{now_second - i}' for i in range(window_seconds)]
        values = conn.mget(keys)

        per_second = []
        total = 0
        max_qps = 0
        for i, val in enumerate(values):
            count = int(val) if val else 0
            total += count
            max_qps = max(max_qps, count)
            per_second.append({
                'second': now_second - i,
                'count': count,
            })

        return {
            'window': window_seconds,
            'total_requests': total,
            'avg_qps': round(total / window_seconds, 2),
            'max_qps': max_qps,
            'per_second': per_second,
        }
    except Exception as e:
        return {'error': str(e)}
