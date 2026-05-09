"""
RabbitMQ Producer - 發送訊息到 queue
"""
import json
import pika
from django.conf import settings


def get_connection():
    # 建立 RabbitMQ 連線
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
    )
    return pika.BlockingConnection(parameters)


def publish(queue_name: str, message: dict, exchange: str = ''):
    """
    將 message 發送到指定 queue
    queue_name: 目標 queue 名稱
    message: 要發送的 dict (會自動轉 JSON)
    exchange: 預設使用 default exchange
    """
    connection = get_connection()
    try:
        channel = connection.channel()
        # 確保 queue 存在 (durable=True 表示 RabbitMQ 重啟後還在)
        channel.queue_declare(queue=queue_name, durable=True)

        channel.basic_publish(
            exchange=exchange,
            routing_key=queue_name,
            body=json.dumps(message, ensure_ascii=False).encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2,  # 訊息持久化
                content_type='application/json',
            ),
        )
    finally:
        connection.close()
