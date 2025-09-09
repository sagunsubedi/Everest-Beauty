from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from products.models import Product, Category, Brand
from .models import Cart, CartItem
from user_management.models import Wishlist
from .serializers import (
    ProductSerializer, CategorySerializer, BrandSerializer,
    CartSerializer, CartItemSerializer, WishlistSerializer
)


class ProductListAPI(generics.ListAPIView):
    """API view for listing products with filtering"""
    queryset = Product.objects.filter(is_active=True).select_related('brand', 'category')
    serializer_class = ProductSerializer
    filterset_fields = ['category', 'brand', 'product_type', 'is_featured', 'is_bestseller']
    search_fields = ['name', 'description', 'brand__name', 'category__name']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']


class ProductDetailAPI(generics.RetrieveAPIView):
    """API view for product detail"""
    queryset = Product.objects.filter(is_active=True).select_related('brand', 'category')
    serializer_class = ProductSerializer
    lookup_field = 'slug'


class CategoryListAPI(generics.ListAPIView):
    """API view for listing categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer


class BrandListAPI(generics.ListAPIView):
    """API view for listing brands"""
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer


class CartAPI(generics.RetrieveAPIView):
    """API view for cart operations"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddToCartAPI(generics.GenericAPIView):
    """API view for adding items to cart"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not product_id:
            return Response(
                {'success': False, 'message': 'Product ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return Response({
            'success': True,
            'message': f'{product.name} added to cart!',
            'cart_count': cart.total_items
        }, status=status.HTTP_200_OK)


class RemoveFromCartAPI(generics.GenericAPIView):
    """API view for removing items from cart"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response(
                {'success': False, 'message': 'Item ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Cart item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        cart_item.delete()
        
        cart = request.user.carts.first()
        return Response({
            'success': True,
            'message': 'Item removed from cart',
            'cart_total': float(cart.total_amount) if cart else 0,
            'subtotal': float(cart.subtotal) if cart else 0
        }, status=status.HTTP_200_OK)


class UpdateCartItemAPI(generics.GenericAPIView):
    """API view for updating cart item quantity"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not item_id:
            return Response(
                {'success': False, 'message': 'Item ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Cart item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if quantity <= 0:
            cart_item.delete()
            message = 'Item removed from cart'
        else:
            cart_item.quantity = quantity
            cart_item.save()
            message = 'Quantity updated'
        
        cart = request.user.carts.first()
        return Response({
            'success': True,
            'message': message,
            'item_total': float(cart_item.total_price) if quantity > 0 else 0,
            'cart_total': float(cart.total_amount) if cart else 0,
            'subtotal': float(cart.subtotal) if cart else 0
        }, status=status.HTTP_200_OK)


class WishlistAPI(generics.ListAPIView):
    """API view for user wishlist"""
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')


class AddToWishlistAPI(generics.GenericAPIView):
    """API view for adding products to wishlist"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response(
                {'success': False, 'message': 'Product ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            message = f'{product.name} added to wishlist!'
        else:
            message = f'{product.name} is already in your wishlist!'
        
        return Response({
            'success': True,
            'message': message
        }, status=status.HTTP_200_OK)


class RemoveFromWishlistAPI(generics.GenericAPIView):
    """API view for removing products from wishlist"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response(
                {'success': False, 'message': 'Product ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            wishlist_item = Wishlist.objects.get(
                user=request.user, 
                product_id=product_id
            )
            product_name = wishlist_item.product.name
            wishlist_item.delete()
            
            return Response({
                'success': True,
                'message': f'{product_name} removed from wishlist!'
            }, status=status.HTTP_200_OK)
        except Wishlist.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Product not found in wishlist'}, 
                status=status.HTTP_404_NOT_FOUND
            )
