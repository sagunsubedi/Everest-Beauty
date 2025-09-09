from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('brand/<slug:slug>/', views.brand_products, name='brand_products'),
    path('search/', views.search_products, name='search_products'),
    path('filter/', views.filter_products, name='filter_products'),
]
