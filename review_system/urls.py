from django.urls import path
from . import views

app_name = 'review_system'

urlpatterns = [
    path('product/<int:product_id>/reviews/', views.product_reviews, name='product_reviews'),
    path('product/<int:product_id>/review/add/', views.add_review, name='add_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('review/<int:review_id>/vote/', views.vote_review, name='vote_review'),
    path('review/<int:review_id>/report/', views.report_review, name='report_review'),
]
