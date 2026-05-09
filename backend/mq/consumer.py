"""
RabbitMQ Consumer - 接收 queue 訊息並處理
"""
import json
import logging
from .producer import get_connection
from .tasks import TASK_REGISTRY

logger = logging.getLogger(__name__)


def _callback(ch, method, properties, body):
    # 訊息處理 callback
    try:
        payload = json.loads(body.decode('utf-8'))
        queue_name = method.routing_key

        # 依 queue 名稱找對應的 handler
        handler = TASK_REGISTRY.get(queue_name)
        if handler:
            handler(payload)
        else:
            logger.warning(f"No handler for queue: {queue_name}")

        # 處理成功 → ack
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.exception(f"Consumer error: {e}")
        # 失敗 → 不 requeue (避免無限迴圈), 可改 True 讓它重試
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consuming(queue_names):
    """
    開始消費指定的 queue 列表
    queue_names: list[str]
    """
    connection = get_connection()
    channel = connection.channel()

    # 一次只取一個訊息, 處理完才拿下一個
    channel.basic_qos(prefetch_count=1)

    for queue_name in queue_names:
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_consume(queue=queue_name, on_message_callback=_callback)
        logger.info(f"Listening on queue: {queue_name}")

    print(f"[*] Waiting for messages on: {queue_names}. CTRL+C to exit.")
    channel.start_consuming()
