from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MemberViewSet

# Router 自動產生 CRUD:
#   GET/POST   /members/
#   GET/PUT/PATCH/DELETE  /members/{id}/
#   POST       /members/login/
router = DefaultRouter()
router.register(r'members', MemberViewSet, basename='member')

urlpatterns = [
    path('', include(router.urls)),
]
