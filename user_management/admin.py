from django.contrib import admin
from .models import UserProfile, Wishlist


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'phone', 'gender', 'skin_type', 'is_verified', 'created_at'
    ]
    list_filter = ['gender', 'is_verified', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'phone']
    list_editable = ['is_verified']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone', 'date_of_birth', 'gender')
        }),
        ('Beauty Profile', {
            'fields': ('skin_type', 'skin_concerns', 'profile_picture')
        }),
        ('Verification', {
            'fields': ('is_verified',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__email', 'product__name']
    readonly_fields = ['added_at']
