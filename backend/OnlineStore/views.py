from rest_framework.response import Response
from rest_framework import status, viewsets, permissions, filters
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from mq.producer import publish

from .models import (
    Category, Brand, Product, ProductVariant,
    Cart, CartItem, Address, Order, Payment, Review,
)
from .serializers import (
    CategorySerializer, BrandSerializer, ProductSerializer, ProductVariantSerializer,
    CartSerializer, CartItemSerializer, AddressSerializer, OrderSerializer,
    PaymentSerializer, ReviewSerializer,
)


# ============================================================
# 原有測試 view (保留)
# ============================================================

class TestView(APIView):
    # 開放給匿名訪問 (測試/壓測用)
    permission_classes = [AllowAny]
    authentication_classes = []  # 完全不做認證, 加快壓測

    def get(self, request):
        publish('send_email', {
            'to': "test",
            'subject': '歡迎加入',
            'body': f'Hi ',
        })
        return Response({'message': 'hello'}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data  # DRF 的 request，自動解析 JSON

        if not data.get('name'):
            return Response(
                {'error': '名稱不能為空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'id': 1, 'name': data['name']},
            status=status.HTTP_201_CREATED
        )


# ============================================================
# ViewSets
# ============================================================

class CategoryViewSet(viewsets.ModelViewSet):
    """分類 CRUD - 讀公開, 寫需登入"""
    queryset = Category.objects.filter(is_active=True).order_by('sort_order', 'id')
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug']
    ordering_fields = ['sort_order', 'id']


class BrandViewSet(viewsets.ModelViewSet):
    """品牌 CRUD - 讀公開, 寫需登入"""
    queryset = Brand.objects.filter(is_active=True).order_by('id')
    serializer_class = BrandSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """商品 CRUD - 讀公開, 寫需登入"""
    queryset = (
        Product.objects
        .select_related('category', 'brand')
        .prefetch_related('images', 'variants')
        .order_by('-created_at')
    )
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug', 'description']
    ordering_fields = ['base_price', 'sales_count', 'rating_avg', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        # ?status=on_sale  過濾商品狀態
        product_status = self.request.query_params.get('status')
        if product_status:
            qs = qs.filter(status=product_status)
        # ?category=1  過濾分類
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)
        return qs


class ProductVariantViewSet(viewsets.ModelViewSet):
    """SKU CRUD - 需登入"""
    queryset = ProductVariant.objects.select_related('product').order_by('id')
    serializer_class = ProductVariantSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        # ?product=1  只取某商品的 variants
        product_id = self.request.query_params.get('product')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs


class CartViewSet(viewsets.ModelViewSet):
    """購物車 CRUD - 只能看自己的"""
    serializer_class = CartSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related('items')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    """購物車品項 CRUD - 只能看自己的"""
    serializer_class = CartItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user).select_related('variant')


class AddressViewSet(viewsets.ModelViewSet):
    """地址簿 CRUD - 只能看自己的"""
    serializer_class = AddressSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-is_default', 'id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """訂單查詢 - 只能看自己的 (寫入透過 service)"""
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'total_amount']

    def get_queryset(self):
        qs = Order.objects.filter(user=self.request.user).prefetch_related('items').order_by('-created_at')
        # ?status=paid  過濾訂單狀態
        order_status = self.request.query_params.get('status')
        if order_status:
            qs = qs.filter(status=order_status)
        return qs


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """付款紀錄查詢 - 只能看自己的"""
    serializer_class = PaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user).order_by('-created_at')


class ReviewViewSet(viewsets.ModelViewSet):
    """商品評論 CRUD - 讀公開, 寫需登入"""
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating']

    def get_queryset(self):
        qs = Review.objects.filter(is_visible=True).select_related('user', 'product').order_by('-created_at')
        # ?product=1  只取某商品的評論
        product_id = self.request.query_params.get('product')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        return super().perform_destroy(instance)
    
    def perform_update(self, serializer):
        return super().perform_update(serializer)