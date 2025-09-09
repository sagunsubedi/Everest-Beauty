from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    helpful_votes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'product']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating}★)"
    
    def save(self, *args, **kwargs):
        # Check if user has purchased this product
        if not self.is_verified_purchase:
            from order_management.models import Order, OrderItem
            purchased = OrderItem.objects.filter(
                order__user=self.user,
                order__status__in=['delivered', 'completed'],
                product_sku=self.product.sku
            ).exists()
            self.is_verified_purchase = purchased
        super().save(*args, **kwargs)


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='review_images/')
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Review Image'
        verbose_name_plural = 'Review Images'
    
    def __str__(self):
        return f"Image for {self.review}"


class ReviewVote(models.Model):
    VOTE_CHOICES = [
        ('helpful', 'Helpful'),
        ('not_helpful', 'Not Helpful'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_votes')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=20, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'review']
        verbose_name = 'Review Vote'
        verbose_name_plural = 'Review Votes'
    
    def __str__(self):
        return f"{self.user.email} - {self.vote_type} on {self.review}"
    
    def save(self, *args, **kwargs):
        # Update helpful votes count
        if self.vote_type == 'helpful':
            self.review.helpful_votes += 1
        else:
            self.review.helpful_votes = max(0, self.review.helpful_votes - 1)
        self.review.save()
        super().save(*args, **kwargs)
