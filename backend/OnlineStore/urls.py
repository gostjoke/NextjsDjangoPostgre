from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TestView,
    CategoryViewSet, BrandViewSet, ProductViewSet, ProductVariantViewSet,
    CartViewSet, CartItemViewSet, AddressViewSet,
    OrderViewSet, PaymentViewSet, ReviewViewSet,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'variants', ProductVariantViewSet, basename='variant')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cartitem')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    # 測試端點: GET 會丟訊息到 MQ, POST 會驗證 name 欄位
    path('test/', TestView.as_view(), name='onlinestore-test'),
    # ViewSet CRUD
    path('', include(router.urls)),
]
