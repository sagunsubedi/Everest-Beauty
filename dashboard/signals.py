from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import Cart, CartItem


@receiver(user_logged_in)
def merge_carts_on_login(sender, user, request, **kwargs):
    session_key = request.session.session_key
    if not session_key:
        return

    try:
        session_cart = Cart.objects.get(session_key=session_key, user=None)
    except Cart.DoesNotExist:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)

    # Merge items
    for item in session_cart.items.select_related('product').all():
        user_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            product=item.product,
            defaults={'quantity': item.quantity}
        )
        if not created:
            user_item.quantity += item.quantity
            user_item.save()

    # Clear session cart
    session_cart.items.all().delete()
    session_cart.delete()

