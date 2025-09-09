from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from decimal import Decimal
from django.db.models import Avg


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f'/products/category/{self.slug}/'


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    is_nepali_brand = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('skincare', 'Skincare'),
        ('makeup', 'Makeup'),
        ('haircare', 'Haircare'),
        ('fragrance', 'Fragrance'),
        ('tools', 'Tools & Brushes'),
        ('bath', 'Bath & Body'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    sku = models.CharField(max_length=100, unique=True, validators=[
        RegexValidator(regex=r'^[A-Z0-9-]+$', message='SKU must contain only uppercase letters, numbers, and hyphens')
    ])
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    ingredients = models.TextField(blank=True)
    how_to_use = models.TextField(blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    weight_unit = models.CharField(max_length=10, default='g', choices=[
        ('g', 'Grams'),
        ('ml', 'Milliliters'),
        ('oz', 'Ounces'),
    ])
    
    # Product attributes
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_organic = models.BooleanField(default=False)
    is_cruelty_free = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    
    # SEO fields
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.brand.name} - {self.name}"
    
    def get_absolute_url(self):
        return f'/products/{self.slug}/'
    
    @property
    def current_price(self):
        return self.sale_price if self.sale_price else self.price
    
    @property
    def discount_percentage(self):
        if self.sale_price and self.price > self.sale_price:
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0
    
    @property
    def average_rating(self):
        from review_system.models import Review
        avg = Review.objects.filter(product=self, is_verified_purchase=True).aggregate(Avg('rating'))
        return avg['rating__avg'] or 0
    
    @property
    def review_count(self):
        from review_system.models import Review
        return Review.objects.filter(product=self, is_verified_purchase=True).count()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            # Set all other images to non-primary
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)  # e.g., "Shade", "Size", "Formula"
    value = models.CharField(max_length=100)  # e.g., "Nude", "30ml", "Matte"
    sku_suffix = models.CharField(max_length=50, blank=True)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['product', 'name', 'value']
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
    
    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    is_in_stock = models.BooleanField(default=True)
    last_restocked = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'
    
    def __str__(self):
        return f"{self.product.name} - Stock: {self.stock_quantity}"
    
    def save(self, *args, **kwargs):
        self.is_in_stock = self.stock_quantity > 0
        super().save(*args, **kwargs)
    
    @property
    def stock_status(self):
        if self.stock_quantity == 0:
            return 'out_of_stock'
        elif self.stock_quantity <= self.low_stock_threshold:
            return 'low_stock'
        else:
            return 'in_stock'
