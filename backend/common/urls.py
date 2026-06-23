from django.urls import path
from .views import HealthCheckView

urlpatterns = [
    # GET /api/common/health/
    path('health/', HealthCheckView.as_view(), name='health-check'),
]
