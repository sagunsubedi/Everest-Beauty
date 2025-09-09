from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Review, ReviewImage, ReviewVote
from products.models import Product
from order_management.models import Order, OrderItem

@login_required
def product_reviews(request, product_id):
    """Display all reviews for a product"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    reviews = Review.objects.filter(product=product, is_active=True).order_by('-created_at')
    
    # Check if user has purchased this product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status__in=['completed', 'delivered']
    ).exists()
    
    context = {
        'product': product,
        'reviews': reviews,
        'has_purchased': has_purchased,
    }
    return render(request, 'review_system/product_reviews.html', context)

@login_required
def add_review(request, product_id):
    """Add a new review for a product"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Check if user has purchased this product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status__in=['completed', 'delivered']
    ).exists()
    
    if not has_purchased:
        messages.error(request, 'You can only review products you have purchased.')
        return redirect('products:product_detail', slug=product.slug)
    
    # Check if user already reviewed this product
    existing_review = Review.objects.filter(user=request.user, product=product).first()
    if existing_review:
        messages.info(request, 'You have already reviewed this product.')
        return redirect('review_system:edit_review', review_id=existing_review.id)
    
    if request.method == 'POST':
        # Handle review submission form
        # This will be implemented in Phase 5
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        comment = request.POST.get('comment')
        
        if rating and title and comment:
            review = Review.objects.create(
                user=request.user,
                product=product,
                rating=int(rating),
                title=title,
                comment=comment,
                is_verified_purchase=True
            )
            
            # Handle image uploads
            images = request.FILES.getlist('images')
            for image in images[:5]:  # Limit to 5 images
                ReviewImage.objects.create(
                    review=review,
                    image=image
                )
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('products:product_detail', slug=product.slug)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'product': product,
    }
    return render(request, 'review_system/add_review.html', context)

@login_required
def edit_review(request, review_id):
    """Edit an existing review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        # Handle review update form
        # This will be implemented in Phase 5
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        comment = request.POST.get('comment')
        
        if rating and title and comment:
            review.rating = int(rating)
            review.title = title
            review.comment = comment
            review.save()
            
            messages.success(request, 'Review updated successfully!')
            return redirect('products:product_detail', slug=review.product.slug)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'review': review,
    }
    return render(request, 'review_system/edit_review.html', context)

@login_required
def delete_review(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        product_slug = review.product.slug
        review.delete()
        messages.success(request, 'Review deleted successfully!')
        return redirect('products:product_detail', slug=product_slug)
    
    context = {
        'review': review,
    }
    return render(request, 'review_system/delete_review.html', context)

@login_required
def vote_review(request, review_id):
    """Vote on a review (helpful/not helpful)"""
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id)
        vote_type = request.POST.get('vote_type')
        
        if vote_type in ['helpful', 'not_helpful']:
            # Check if user already voted
            existing_vote = ReviewVote.objects.filter(
                user=request.user,
                review=review
            ).first()
            
            if existing_vote:
                if existing_vote.vote_type == vote_type:
                    # Remove vote if clicking same button
                    existing_vote.delete()
                    action = 'removed'
                else:
                    # Update vote
                    existing_vote.vote_type = vote_type
                    existing_vote.save()
                    action = 'updated'
            else:
                # Create new vote
                ReviewVote.objects.create(
                    user=request.user,
                    review=review,
                    vote_type=vote_type
                )
                action = 'added'
            
            # Update review helpful votes count
            review.update_helpful_votes()
            
            return JsonResponse({
                'success': True,
                'action': action,
                'helpful_votes': review.helpful_votes
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def report_review(request, review_id):
    """Report an inappropriate review"""
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id)
        reason = request.POST.get('reason')
        
        if reason:
            # Handle review reporting
            # This will be implemented in Phase 5
            messages.success(request, 'Review reported successfully. We will review it shortly.')
            return redirect('review_system:product_reviews', product_id=review.product.id)
        else:
            messages.error(request, 'Please provide a reason for reporting.')
    
    context = {
        'review': get_object_or_404(Review, id=review_id),
    }
    return render(request, 'review_system/report_review.html', context)

