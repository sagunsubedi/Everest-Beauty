from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('khalti', 'Khalti'),
        ('cod', 'Cash on Delivery'),
    ]
    
    order = models.ForeignKey('order_management.Order', on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.user.email}"


class KhaltiTransaction(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='khalti_transaction')
    khalti_token = models.CharField(max_length=255)
    khalti_payment_id = models.CharField(max_length=100, blank=True)
    khalti_amount = models.DecimalField(max_digits=10, decimal_places=2)
    khalti_status = models.CharField(max_length=50, blank=True)
    khalti_response = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Khalti Transaction'
        verbose_name_plural = 'Khalti Transactions'
    
    def __str__(self):
        return f"Khalti: {self.khalti_payment_id} - {self.payment.user.email}"


## eSewa models removed
