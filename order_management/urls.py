from django.urls import path
from . import views

app_name = 'order_management'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/tracking/', views.order_tracking, name='order_tracking'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('shipping-address/', views.shipping_address, name='shipping_address'),
    path('shipping-address/<int:address_id>/edit/', views.edit_shipping_address, name='edit_shipping_address'),
]
