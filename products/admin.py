from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, ProductVariant, Inventory


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['name', 'value', 'sku_suffix', 'price_adjustment', 'is_active']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_nepali_brand', 'is_active', 'created_at']
    list_filter = ['is_nepali_brand', 'is_active', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'brand', 'category', 'product_type', 'price', 'sale_price',
        'is_featured', 'is_bestseller', 'is_active', 'created_at'
    ]
    list_filter = [
        'brand', 'category', 'product_type', 'is_featured', 'is_bestseller',
        'is_new_arrival', 'is_organic', 'is_cruelty_free', 'is_vegan',
        'is_active', 'created_at'
    ]
    search_fields = ['name', 'sku', 'brand__name', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured', 'is_bestseller', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'brand', 'category', 'product_type')
        }),
        ('Description', {
            'fields': ('description', 'short_description', 'ingredients', 'how_to_use')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price')
        }),
        ('Product Details', {
            'fields': ('weight', 'weight_unit')
        }),
        ('Attributes', {
            'fields': ('is_featured', 'is_bestseller', 'is_new_arrival', 'is_organic', 'is_cruelty_free', 'is_vegan')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'stock_quantity', 'low_stock_threshold', 'is_in_stock', 'last_restocked']
    list_filter = ['is_in_stock', 'last_restocked']
    search_fields = ['product__name', 'product__sku']
    list_editable = ['stock_quantity', 'low_stock_threshold']
    readonly_fields = ['is_in_stock', 'last_restocked']
