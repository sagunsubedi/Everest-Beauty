from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category, Brand

# Create your views here.

def product_list(request):
    """Display all products with optional filtering"""
    products = Product.objects.filter(is_active=True)
    
    # Get filter parameters
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    
    if category:
        products = products.filter(category__slug=category)
    if brand:
        products = products.filter(brand__slug=brand)
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    
    context = {
        'products': products,
        'categories': Category.objects.filter(is_active=True),
        'brands': Brand.objects.filter(is_active=True),
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    """Display detailed product information"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)

def category_products(request, slug):
    """Display products from a specific category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/category_products.html', context)

def brand_products(request, slug):
    """Display products from a specific brand"""
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    products = Product.objects.filter(brand=brand, is_active=True)
    
    context = {
        'brand': brand,
        'products': products,
    }
    return render(request, 'products/brand_products.html', context)

def search_products(request):
    """Search products by name, description, or brand"""
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query),
            is_active=True
        )
    
    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'products/search_results.html', context)

def filter_products(request):
    """Filter products by various criteria"""
    products = Product.objects.filter(is_active=True)
    
    # Apply filters
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    product_type = request.GET.get('product_type')
    
    if category:
        products = products.filter(category__slug=category)
    if brand:
        products = products.filter(brand__slug=brand)
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    if product_type:
        products = products.filter(product_type=product_type)
    
    context = {
        'products': products,
        'categories': Category.objects.filter(is_active=True),
        'brands': Brand.objects.filter(is_active=True),
    }
    return render(request, 'products/filtered_products.html', context)
