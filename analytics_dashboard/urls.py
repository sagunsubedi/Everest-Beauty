"""
URL configuration for Everest Beauty e-commerce platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/', include('dashboard.api_urls')),
    path('', include('dashboard.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('order_management.urls')),
    path('users/', include('user_management.urls')),
    path('payments/', include('payment_gateway.urls')),
    path('reviews/', include('review_system.urls')),
    

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site configuration
admin.site.site_header = "Everest Beauty Admin"
admin.site.site_title = "Everest Beauty Admin Portal"
admin.site.index_title = "Welcome to Everest Beauty Admin Portal"
