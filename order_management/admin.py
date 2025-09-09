from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['product_name', 'product_sku', 'quantity', 'unit_price', 'total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'total_amount', 'payment_method',
        'payment_status', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__email', 'shipping_phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    list_editable = ['status', 'payment_status']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'total_amount')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'shipping_phone', 'shipping_email')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'city', 'state', 'is_default', 'created_at']
    list_filter = ['is_default', 'city', 'state', 'created_at']
    search_fields = ['user__email', 'full_name', 'city', 'state']
    list_editable = ['is_default']
    readonly_fields = ['created_at']
