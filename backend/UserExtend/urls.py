"""
URL routes - 用 DRF Router 自動產生 CRUD URL
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

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
    # auth endpoints
    path('auth/login/', views.login_view, name='auth-login'),
    path('auth/logout/', views.logout_view, name='auth-logout'),
    # CRUD endpoints
    path('', include(router.urls)),
]
