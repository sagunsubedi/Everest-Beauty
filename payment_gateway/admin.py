from django.contrib import admin
from .models import Payment, KhaltiTransaction


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'user', 'order', 'amount', 'payment_method',
        'status', 'payment_date'
    ]
    list_filter = ['payment_method', 'status', 'payment_date']
    search_fields = ['transaction_id', 'user__email', 'order__order_number']
    readonly_fields = ['payment_date', 'updated_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('transaction_id', 'order', 'user', 'amount', 'payment_method')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('payment_date', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(KhaltiTransaction)
class KhaltiTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'payment', 'khalti_payment_id', 'khalti_amount', 'khalti_status', 'created_at'
    ]
    list_filter = ['khalti_status', 'created_at']
    search_fields = ['khalti_payment_id', 'payment__user__email']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('payment', 'khalti_token', 'khalti_payment_id', 'khalti_amount')
        }),
        ('Status', {
            'fields': ('khalti_status',)
        }),
        ('Response Data', {
            'fields': ('khalti_response',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )


## eSewa removed
