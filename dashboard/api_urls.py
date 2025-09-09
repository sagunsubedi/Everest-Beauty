from django.urls import path
from . import api_views

app_name = 'dashboard_api'

urlpatterns = [
    path('products/', api_views.ProductListAPI.as_view(), name='product_list'),
    path('products/<slug:slug>/', api_views.ProductDetailAPI.as_view(), name='product_detail'),
    path('categories/', api_views.CategoryListAPI.as_view(), name='category_list'),
    path('brands/', api_views.BrandListAPI.as_view(), name='brand_list'),
    path('cart/', api_views.CartAPI.as_view(), name='cart_api'),
    path('cart/add/', api_views.AddToCartAPI.as_view(), name='add_to_cart_api'),
    path('cart/remove/', api_views.RemoveFromCartAPI.as_view(), name='remove_from_cart_api'),
    path('cart/update/', api_views.UpdateCartItemAPI.as_view(), name='update_cart_item_api'),
    path('wishlist/', api_views.WishlistAPI.as_view(), name='wishlist_api'),
    path('wishlist/add/', api_views.AddToWishlistAPI.as_view(), name='add_to_wishlist_api'),
    path('wishlist/remove/', api_views.RemoveFromWishlistAPI.as_view(), name='remove_from_wishlist_api'),
]
