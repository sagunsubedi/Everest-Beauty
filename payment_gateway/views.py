from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment, KhaltiTransaction
from order_management.models import Order
import json
import requests

@login_required
def khalti_initiate(request):
    """Initiate Khalti payment"""
    if request.method == 'POST':
        order_id = request.POST.get('order_id') or request.GET.get('order_id')
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            
            # Khalti payment initiation logic
            # This will be implemented in Phase 6
            khalti_data = {
                'public_key': 'test_public_key',  # Replace with actual key
                'amount': int(order.total_amount * 100),  # Convert to paisa
                'product_identity': str(order.id),
                'product_name': f'Order #{order.order_number}',
                'customer_info': {
                    'name': request.user.get_full_name() or request.user.username,
                    'email': request.user.email,
                }
            }
            
            # Store payment record
            payment = Payment.objects.create(
                order=order,
                user=request.user,
                amount=order.total_amount,
                payment_method='khalti',
                status='pending'
            )
            
            return JsonResponse({'success': True, 'payment_id': payment.id, 'khalti': khalti_data})
            
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def khalti_verify(request):
    """Verify Khalti payment"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            payment_id = data.get('payment_id')
            
            # Verify payment with Khalti API
            from django.conf import settings
            verification_url = f"{settings.KHALTI_BASE_URL}/payment/verify/"
            response = requests.post(verification_url, headers={
                'Authorization': f"Key {settings.KHALTI_SECRET_KEY}",
            }, data={
                'token': token,
                'amount': data.get('amount')
            }, timeout=15)

            if response.status_code == 200:
                payment = Payment.objects.get(id=payment_id)
                payment.status = 'completed'
                payment.transaction_id = response.json().get('idx', '')
                payment.save()

                # Update order status
                order = payment.order
                order.status = 'confirmed'
                order.payment_status = 'completed'
                order.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': response.text})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def _get_khalti_headers(request):
    from django.conf import settings
    return {
        'Authorization': f'Key {settings.KHALTI_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

@login_required
def cod_initiate(request):
    """Initiate Cash on Delivery: create a pending Payment and mark order as confirmed."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    order_id = request.POST.get('order_id')
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            amount=order.total_amount,
            payment_method='cod',
            status='processing'
        )
        order.status = 'confirmed'
        order.payment_status = 'pending'
        order.save()
        return JsonResponse({'success': True, 'payment_id': payment.id, 'redirect_url': f"/payments/payment/success/{payment.id}/"})
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'})

@login_required
def payment_success(request, payment_id):
    """Handle successful payment"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'payment_gateway/payment_success.html', context)

@login_required
def payment_failure(request, payment_id):
    """Handle failed payment"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'payment_gateway/payment_failure.html', context)

@login_required
def payment_cancel(request, payment_id):
    """Handle cancelled payment"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Update payment status
    payment.status = 'cancelled'
    payment.save()
    
    # Update order status
    order = payment.order
    order.status = 'cancelled'
    order.save()
    
    messages.info(request, 'Payment was cancelled.')
    return redirect('order_management:order_detail', order_id=order.id)
