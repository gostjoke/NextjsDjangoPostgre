"""
OnlineStore database schema
Covers common e-commerce scenarios: Category / Brand / Product / SKU Variant /
                                     Images / Cart / Address / Order / OrderItem /
                                     Payment / Review
"""
from django.db import models
from django.contrib.auth.models import User


# ============================================================
# Product related
# ============================================================

class Category(models.Model):
    """Product category (supports hierarchy, e.g. Apparel > Men > T-shirt)"""
    name = models.CharField(max_length=100, verbose_name='Category Name')
    slug = models.SlugField(max_length=120, unique=True)
    # self relation for tree structure
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='children',
        verbose_name='Parent Category',
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Brand(models.Model):
    """Brand"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Brand Name')
    logo = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product (master record)"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('on_sale', 'On Sale'),
        ('off_sale', 'Off Sale'),
        ('sold_out', 'Sold Out'),
    ]

    name = models.CharField(max_length=200, verbose_name='Product Name')
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True, verbose_name='Description')
    short_description = models.CharField(max_length=300, blank=True)
    # Relations
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT,
        related_name='products', verbose_name='Category',
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products',
    )
    # Pricing (base price, each variant can override)
    base_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Base Price',
    )
    cost_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='Cost Price',
    )
    # Status
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft',
    )
    is_featured = models.BooleanField(default=False, verbose_name='Featured')
    # Stats (denormalized for query speed)
    sales_count = models.IntegerField(default=0, verbose_name='Sales Count')
    view_count = models.IntegerField(default=0, verbose_name='View Count')
    rating_avg = models.DecimalField(
        max_digits=3, decimal_places=2, default=0, verbose_name='Average Rating',
    )
    rating_count = models.IntegerField(default=0)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', 'status']),
        ]

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """Product image (one product, multiple images)"""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images',
    )
    image_url = models.URLField()
    alt_text = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False, verbose_name='Main Image')
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['sort_order', 'id']


class ProductVariant(models.Model):
    """Product variant / SKU (e.g. same T-shirt in red size M)"""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='variants',
    )
    sku = models.CharField(max_length=64, unique=True, verbose_name='SKU')
    # Variant attributes (JSON for flexibility: {"size": "M", "color": "red"})
    attributes = models.JSONField(default=dict, blank=True)
    # Each SKU has its own price and stock
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0, verbose_name='Stock')
    # Safety stock (alert when below)
    safety_stock = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'SKU'
        verbose_name_plural = 'SKUs'
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['product', 'is_active']),
        ]

    def __str__(self):
        return f'{self.product.name} - {self.sku}'


# ============================================================
# Cart
# ============================================================

class Cart(models.Model):
    """Shopping cart (one per user)"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='cart',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'


class CartItem(models.Model):
    """Cart item"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        # Same user + same SKU has only one row (quantity accumulates)
        unique_together = [('cart', 'variant')]


# ============================================================
# Address
# ============================================================

class Address(models.Model):
    """User address book"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='addresses',
    )
    recipient_name = models.CharField(max_length=50, verbose_name='Recipient Name')
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default='Taiwan')
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50, blank=True)
    street = models.CharField(max_length=200)
    zip_code = models.CharField(max_length=10, blank=True)
    is_default = models.BooleanField(default=False, verbose_name='Default Address')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.recipient_name} - {self.city}{self.street}'


# ============================================================
# Order
# ============================================================

class Order(models.Model):
    """Order master record"""
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    # Order number for display (e.g. ORD20260510-00001)
    order_no = models.CharField(max_length=40, unique=True, verbose_name='Order No')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='orders',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending',
    )
    # Split amounts for reconciliation
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Subtotal')
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total Amount')
    # Shipping info (snapshot at order time, not FK to Address - keeps history if address deleted)
    recipient_name = models.CharField(max_length=50)
    recipient_phone = models.CharField(max_length=20)
    shipping_address = models.CharField(max_length=300)
    # Note
    note = models.TextField(blank=True)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['order_no']),
        ]

    def __str__(self):
        return self.order_no


class OrderItem(models.Model):
    """Order item (snapshot at order time, not dependent on live Product/Variant)"""
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items',
    )
    # PROTECT: prevent deleting variants with orders
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    # Snapshot fields: even if product is renamed/repriced later, history is preserved
    product_name = models.CharField(max_length=200)
    sku = models.CharField(max_length=64)
    attributes_snapshot = models.JSONField(default=dict, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Unit Price at Order')
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'


# ============================================================
# Payment
# ============================================================

class Payment(models.Model):
    """Payment record (an order may have multiple payment attempts)"""
    METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('atm', 'ATM Transfer'),
        ('line_pay', 'LINE Pay'),
        ('apple_pay', 'Apple Pay'),
        ('cod', 'Cash on Delivery'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='payments',
    )
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Third-party gateway transaction id
    transaction_id = models.CharField(max_length=100, blank=True)
    # Raw response for debugging
    response_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']


# ============================================================
# Review
# ============================================================

class Review(models.Model):
    """Product review (only after purchase)"""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews',
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='reviews',
    )
    # Link to specific order item to prevent duplicate reviews
    order_item = models.OneToOneField(
        OrderItem, on_delete=models.CASCADE, related_name='review',
    )
    rating = models.PositiveSmallIntegerField()  # 1~5
    title = models.CharField(max_length=100, blank=True)
    content = models.TextField(blank=True)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
        ]
