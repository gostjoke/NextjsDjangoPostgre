"""
OnlineStore Admin 註冊
"""
from django.contrib import admin
from .models import (
    Category, Brand, Product, ProductImage, ProductVariant,
    Cart, CartItem, Address,
    Order, OrderItem, Payment, Review,
)


# ===== Inline (在父 model 編輯頁直接編輯子 model) =====

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'sku', 'unit_price', 'quantity', 'subtotal')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


# ===== 主註冊 =====

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'created_at')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'brand', 'base_price', 'status', 'sales_count')
    list_filter = ('status', 'is_featured', 'category', 'brand')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    readonly_fields = ('sales_count', 'view_count', 'rating_avg', 'rating_count')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku', 'product', 'price', 'stock', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('sku', 'product__name')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'updated_at')
    inlines = [CartItemInline]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipient_name', 'phone', 'city', 'is_default')
    list_filter = ('is_default', 'city')
    search_fields = ('recipient_name', 'phone', 'user__username')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_no', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_no', 'user__username', 'recipient_name')
    inlines = [OrderItemInline]
    readonly_fields = ('order_no', 'created_at', 'paid_at', 'shipped_at', 'completed_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'method', 'status', 'amount', 'created_at')
    list_filter = ('method', 'status')
    search_fields = ('order__order_no', 'transaction_id')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rating', 'is_visible', 'created_at')
    list_filter = ('rating', 'is_visible')
    search_fields = ('product__name', 'user__username')
