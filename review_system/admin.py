from django.contrib import admin
from .models import Review, ReviewImage, ReviewVote


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    fields = ['image', 'caption']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'product', 'rating', 'title', 'is_verified_purchase',
        'helpful_votes', 'created_at'
    ]
    list_filter = [
        'rating', 'is_verified_purchase', 'created_at'
    ]
    search_fields = ['user__email', 'product__name', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_verified_purchase']
    inlines = [ReviewImageInline]
    
    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'product', 'rating', 'title', 'comment')
        }),
        ('Verification', {
            'fields': ('is_verified_purchase',)
        }),
        ('Engagement', {
            'fields': ('helpful_votes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'review', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    search_fields = ['user__email', 'review__title']
    readonly_fields = ['created_at']
