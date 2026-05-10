from django.urls import path
from .views import MQtestView

urlpatterns = [
    # 發送訊息到 queue
    path('publish/', MQtestView.as_view(), name='mq-publish'),
]
