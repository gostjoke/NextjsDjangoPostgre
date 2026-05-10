from django.urls import path
from .views import EHSMainTableDetailView

urlpatterns = [
    # 發送訊息到 queue
    path('publish/', EHSMainTableDetailView.as_view(), name='mq-publish'),
]
