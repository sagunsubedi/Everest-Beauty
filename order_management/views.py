from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Order, OrderItem, ShippingAddress
from dashboard.models import Cart
from payment_gateway.models import Payment

@login_required
def checkout(request):
    """Handle checkout process"""
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.is_empty:
        messages.warning(request, 'Your cart is empty.')
        return redirect('dashboard:cart')
    
    if request.method == 'POST':
        # Create order from cart
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        province = request.POST.get('province', '').strip()
        delivery_method = request.POST.get('delivery_method', 'standard')
        payment_method = request.POST.get('payment_method', 'khalti')

        if not (first_name and last_name and phone and address and city and province):
            return JsonResponse({'success': False, 'message': 'Please fill all required fields.'})

        # Compute delivery fee
        subtotal = cart.total_amount
        delivery_fee = 0
        if delivery_method == 'express':
            delivery_fee = 200
        elif delivery_method == 'standard':
            delivery_fee = 0 if subtotal >= 1000 else 100

        order_total = subtotal + delivery_fee

        from .models import Order, OrderItem
        try:
            order = Order.objects.create(
                user=request.user,
                status='pending',
                total_amount=order_total,
                shipping_address=f"{first_name} {last_name}\n{address}\n{city}, {province} {postal_code}",
                shipping_phone=phone,
                shipping_email=request.user.email,
                payment_method=payment_method,
                payment_status='pending',
            )

            # Create order items
            for item in cart.items.select_related('product').all():
                OrderItem.objects.create(
                    order=order,
                    product_name=item.product.name,
                    product_sku=item.product.sku,
                    quantity=item.quantity,
                    unit_price=item.product.current_price,
                    total_price=item.total_price,
                )

            # Clear cart
            cart.items.all().delete()

            return JsonResponse({'success': True, 'order_id': order.id})
        except Exception as exc:
            return JsonResponse({'success': False, 'message': str(exc)})
    
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
        'shipping_addresses': ShippingAddress.objects.filter(user=request.user),
        'KHALTI_PUBLIC_KEY': settings.KHALTI_PUBLIC_KEY,
    }
    return render(request, 'order_management/checkout.html', context)

@login_required
def order_detail(request, order_id):
    """Display order details"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'order_management/order_detail.html', context)

@login_required
def order_list(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'order_management/order_list.html', context)

@login_required
def order_tracking(request, order_id):
    """Display order tracking information"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'order_management/order_tracking.html', context)

@login_required
def cancel_order(request, order_id):
    """Cancel an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'Order cannot be cancelled at this stage.')
    
    return redirect('order_management:order_detail', order_id=order_id)

@login_required
def shipping_address(request):
    """Manage shipping addresses"""
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    context = {
        'addresses': addresses,
    }
    return render(request, 'order_management/shipping_address.html', context)

@login_required
def edit_shipping_address(request, address_id):
    """Edit a shipping address"""
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        # Handle address update form
        # This will be implemented in Phase 5
        pass
    
    context = {
        'address': address,
    }
    return render(request, 'order_management/edit_shipping_address.html', context)
