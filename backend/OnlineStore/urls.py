from django.urls import path
from .views import TestView

urlpatterns = [
    # 測試端點: GET 會丟訊息到 MQ, POST 會驗證 name 欄位
    path('test/', TestView.as_view(), name='onlinestore-test'),
]
