"""
RabbitMQ Producer - 發送訊息到 queue
特色:
- thread-local 連線重用 (不是全域單例, 避免多執行緒衝突)
- 自動重連
- queue_declare 快取 (同一連線只 declare 一次)
- publisher confirm 模式 (確保訊息真的進 queue)
- 失敗時 raise 自訂錯誤, view 可 try/except
"""
import json
import logging
import threading
import pika
from django.conf import settings

logger = logging.getLogger(__name__)

# thread-local 儲存, 每條 thread 自己一條連線 (pika 不是 thread-safe)
_local = threading.local()


class PublishError(Exception):
    """發送失敗 (連線錯誤 / broker 拒收)"""
    pass


def _build_connection():
    # 建立新連線
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER,
        settings.RABBITMQ_PASSWORD,
    )
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        virtual_host=settings.RABBITMQ_VHOST,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300,
        socket_timeout=5,  # 連不上 5 秒就放棄, 避免 view 卡死
    )
    return pika.BlockingConnection(parameters)


def _get_channel():
    """取得當前 thread 的 channel, 沒有就建立"""
    conn = getattr(_local, 'connection', None)
    channel = getattr(_local, 'channel', None)
    declared = getattr(_local, 'declared_queues', None)

    # 連線斷了或不存在 → 重建
    if conn is None or conn.is_closed:
        conn = _build_connection()
        channel = conn.channel()
        channel.confirm_delivery()  # 開啟 publisher confirm
        declared = set()
        _local.connection = conn
        _local.channel = channel
        _local.declared_queues = declared

    return channel, declared


def publish(queue_name: str, message: dict, exchange: str = ''):
    """
    將 message 發送到指定 queue
    成功: 回 True
    失敗: raise PublishError
    """
    try:
        channel, declared = _get_channel()

        # 同一 channel 只 declare 一次 (省 round trip)
        if queue_name not in declared:
            channel.queue_declare(queue=queue_name, durable=True)
            declared.add(queue_name)

        channel.basic_publish(
            exchange=exchange,
            routing_key=queue_name,
            body=json.dumps(message, ensure_ascii=False).encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2,  # 訊息持久化
                content_type='application/json',
            ),
            mandatory=True,  # 找不到 queue 時 broker 會回退
        )
        return True

    except (pika.exceptions.AMQPError, pika.exceptions.ConnectionClosed) as e:
        # 連線炸了 → 清掉 cache, 下次 publish 會重連
        logger.exception(f"Publish failed: {e}")
        _reset()
        raise PublishError(str(e))
    except Exception as e:
        logger.exception(f"Unexpected publish error: {e}")
        _reset()
        raise PublishError(str(e))


def _reset():
    """清掉壞掉的連線"""
    try:
        conn = getattr(_local, 'connection', None)
        if conn and not conn.is_closed:
            conn.close()
    except Exception:
        pass
    _local.connection = None
    _local.channel = None
    _local.declared_queues = None


# consumer.py 還是會用到, 保留
def get_connection():
    """單純建立新連線 (consumer 用)"""
    return _build_connection()
