from rest_framework import serializers
from .models import (
    Category, Brand, Product, ProductImage, ProductVariant,
    Cart, CartItem, Address, Order, OrderItem, Payment, Review,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'is_active', 'sort_order', 'created_at']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'logo', 'description', 'is_active', 'created_at']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'is_main', 'sort_order']


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'attributes', 'price', 'stock', 'safety_stock', 'is_active', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    # 巢狀讀取, 寫入仍用 id
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'category', 'brand', 'base_price', 'cost_price', 'status',
            'is_featured', 'sales_count', 'view_count', 'rating_avg', 'rating_count',
            'created_at', 'updated_at', 'images', 'variants',
        ]
        read_only_fields = ['sales_count', 'view_count', 'rating_avg', 'rating_count', 'created_at', 'updated_at']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'quantity', 'added_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'recipient_name', 'phone', 'country',
            'city', 'district', 'street', 'zip_code', 'is_default', 'created_at',
        ]
        read_only_fields = ['created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'variant', 'product_name', 'sku',
            'attributes_snapshot', 'unit_price', 'quantity', 'subtotal',
        ]
        read_only_fields = ['product_name', 'sku', 'attributes_snapshot', 'unit_price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_no', 'status', 'subtotal', 'shipping_fee', 'discount',
            'total_amount', 'recipient_name', 'recipient_phone', 'shipping_address',
            'note', 'created_at', 'paid_at', 'shipped_at', 'completed_at', 'items',
        ]
        read_only_fields = [
            'order_no', 'subtotal', 'shipping_fee', 'discount', 'total_amount',
            'paid_at', 'shipped_at', 'completed_at', 'created_at',
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'method', 'status', 'amount', 'transaction_id', 'created_at', 'paid_at']
        read_only_fields = ['status', 'transaction_id', 'created_at', 'paid_at']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'product', 'order_item', 'rating', 'title', 'content', 'is_visible', 'created_at']
        read_only_fields = ['is_visible', 'created_at']
