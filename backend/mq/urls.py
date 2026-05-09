from django.urls import path
from . import views

urlpatterns = [
    # 發送訊息到 queue
    path('publish/', views.publish_message, name='mq-publish'),
]
