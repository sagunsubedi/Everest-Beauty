from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile, Wishlist
from order_management.models import Order, ShippingAddress

@login_required
def user_profile(request):
    """Display user profile"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = None
    
    context = {
        'profile': profile,
    }
    return render(request, 'user_management/user_profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        # Handle profile update form
        # This will be implemented in Phase 5
        pass
    
    context = {
        'profile': profile,
    }
    return render(request, 'user_management/edit_profile.html', context)

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('user_management:user_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'user_management/change_password.html', context)

@login_required
def user_orders(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'user_management/user_orders.html', context)

@login_required
def user_wishlist(request):
    """Display user's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user).order_by('-added_at')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'user_management/user_wishlist.html', context)

@login_required
def user_addresses(request):
    """Manage user addresses"""
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    context = {
        'addresses': addresses,
    }
    return render(request, 'user_management/user_addresses.html', context)

@login_required
def add_address(request):
    """Add new shipping address"""
    if request.method == 'POST':
        # Handle address creation form
        # This will be implemented in Phase 5
        pass
    
    return render(request, 'user_management/add_address.html')

@login_required
def edit_address(request, address_id):
    """Edit shipping address"""
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        # Handle address update form
        # This will be implemented in Phase 5
        pass
    
    context = {
        'address': address,
    }
    return render(request, 'user_management/edit_address.html', context)

@login_required
def delete_address(request, address_id):
    """Delete shipping address"""
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully.')
        return redirect('user_management:user_addresses')
    
    context = {
        'address': address,
    }
    return render(request, 'user_management/delete_address.html', context)
