"""
Task handlers - 把 queue name 對應到處理函式
新增任務時, 寫一個 function 然後註冊到 TASK_REGISTRY
"""
import logging

logger = logging.getLogger(__name__)


# 範例: 處理 email 寄送任務
def handle_send_email(payload: dict):
    to = payload.get('to')
    subject = payload.get('subject')
    logger.info(f"[send_email] to={to} subject={subject}")
    # TODO: 真正寄信邏輯放這裡 (例如 django.core.mail.send_mail)


# 範例: 處理通知任務
def handle_notification(payload: dict):
    user_id = payload.get('user_id')
    message = payload.get('message')
    logger.info(f"[notification] user={user_id} msg={message}")
    # TODO: 寫 DB 或推播


# queue name -> handler 對應表
TASK_REGISTRY = {
    'send_email': handle_send_email,
    'notification': handle_notification,
}
