"""
URL routes - 用 DRF Router 自動產生 CRUD URL
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views
from .jwt_views import JWTLoginView

# Router 會自動產生:
#   GET    /users/         list
#   POST   /users/         create
#   GET    /users/{id}/    retrieve
#   PUT    /users/{id}/    update
#   PATCH  /users/{id}/    partial_update
#   DELETE /users/{id}/    destroy
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'userinfos', views.UserInfoViewSet, basename='userinfo')

urlpatterns = [
    # Token-based 登入 (回傳 DRF Token)
    path('auth/login/', views.login_view, name='auth-login'),
    path('auth/logout/', views.logout_view, name='auth-logout'),
    # JWT-based 登入 (回傳 access + refresh + user 資料)
    path('auth/jwt/login/', JWTLoginView.as_view(), name='jwt-login'),
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),
    path('auth/jwt/verify/', TokenVerifyView.as_view(), name='jwt-verify'),
    # CRUD endpoints
    path('', include(router.urls)),
]
