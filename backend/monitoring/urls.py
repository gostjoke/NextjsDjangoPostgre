from django.urls import path
from .views import QPSView

urlpatterns = [
    # GET /api/monitoring/qps/?window=10
    path('qps/', QPSView.as_view(), name='qps'),
]
