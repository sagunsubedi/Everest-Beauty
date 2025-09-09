from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.forms import UserCreationForm
from review_system.models import Review
from products.models import Product, Category, Brand
from .models import Cart, CartItem, Banner
from user_management.models import Wishlist
import json

def admin_dashboard(request):
    User = get_user_model()
    total_products = Product.objects.count()
    total_users = User.objects.count()
    total_reviews = Review.objects.count()
    recent_users = User.objects.order_by('-date_joined')[:5]
    context = {
        'total_products': total_products,
        'total_users': total_users,
        'total_reviews': total_reviews,
        'recent_users': recent_users,
    }
    return render(request, 'admin_dashboard.html', context)
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('account_login')
    else:
        form = UserCreationForm()
    return render(request, 'account/signup.html', {'form': form})

@ensure_csrf_cookie
def home(request):
    """Homepage view with featured products and banners"""
    featured_products = Product.objects.filter(
        is_featured=True, 
        is_active=True
    ).select_related('brand', 'category')[:8]
    
    bestseller_products = Product.objects.filter(
        is_bestseller=True, 
        is_active=True
    ).select_related('brand', 'category')[:6]
    
    new_arrivals = Product.objects.filter(
        is_new_arrival=True, 
        is_active=True
    ).select_related('brand', 'category')[:6]
    
    now = timezone.now()
    hero_banners = (
        Banner.objects.filter(
            banner_type='hero',
            is_active=True
        )
        .filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now),
            Q(end_date__isnull=True) | Q(end_date__gte=now),
        )
        .order_by('order')[:3]
    )
    
    categories = Category.objects.filter(is_active=True, parent=None)[:6]
    
    context = {
        'featured_products': featured_products,
        'bestseller_products': bestseller_products,
        'new_arrivals': new_arrivals,
        'hero_banners': hero_banners,
        'categories': categories,
    }
    
    return render(request, 'dashboard/home.html', context)


def about(request):
    """About page view"""
    return render(request, 'dashboard/about.html')


def contact(request):
    """Contact page view"""
    return render(request, 'dashboard/contact.html')


def search_products(request):
    """Product search view"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    brand = request.GET.get('brand', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    
    products = Product.objects.filter(is_active=True).select_related('brand', 'category')
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    if category:
        products = products.filter(category__slug=category)
    
    if brand:
        products = products.filter(brand__slug=brand)
    
    if price_min:
        products = products.filter(price__gte=price_min)
    
    if price_max:
        products = products.filter(price__lte=price_max)
    
    # Get filter options
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'query': query,
        'categories': categories,
        'brands': brands,
        'selected_category': category,
        'selected_brand': brand,
        'price_min': price_min,
        'price_max': price_max,
    }
    
    return render(request, 'dashboard/search_results.html', context)


def cart_view(request):
    """Shopping cart view"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    
    return render(request, 'dashboard/cart.html', context)


def add_to_cart(request, product_id):
    """Add product to cart"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        quantity = int(request.POST.get('quantity', 1))
        
        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart!')
        # Treat fetch() requests as AJAX even if X-Requested-With is not set
        if (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            or 'application/json' in (request.headers.get('Accept') or '')
        ):
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart!',
                'cart_count': cart.total_items
            })
        return redirect('dashboard:cart')

    # If not POST, force JSON error for AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
    return redirect('dashboard:cart')


def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if request.user.is_authenticated:
        if cart_item.cart.user == request.user:
            product_name = cart_item.product.name
            cart_item.delete()
            messages.success(request, f'{product_name} removed from cart!')
    else:
        if cart_item.cart.session_key == request.session.session_key:
            product_name = cart_item.product.name
            cart_item.delete()
            messages.success(request, f'{product_name} removed from cart!')
    
    return redirect('dashboard:cart')


def update_cart_item(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated!')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')
    
    return redirect('dashboard:cart')


@login_required
def wishlist_view(request):
    """User wishlist view"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    
    return render(request, 'dashboard/wishlist.html', context)


@login_required
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f'{product.name} added to wishlist!')
    else:
        messages.info(request, f'{product.name} is already in your wishlist!')
    
    return redirect('dashboard:wishlist')


@login_required
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        messages.success(request, f'{product.name} removed from wishlist!')
    except Wishlist.DoesNotExist:
        messages.error(request, 'Product not found in wishlist!')
    
    return redirect('dashboard:wishlist')


def get_or_create_cart(request):
    """Helper function to get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        
        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            user=None
        )
    
    return cart


def custom_logout(request):
    """Simple custom logout view"""
    logout(request)
    messages.success(request, 'You have been successfully signed out.')
    return redirect('dashboard:home')