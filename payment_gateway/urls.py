from django.urls import path
from . import views

app_name = 'payment_gateway'

urlpatterns = [
    path('khalti/initiate/', views.khalti_initiate, name='khalti_initiate'),
    path('khalti/verify/', views.khalti_verify, name='khalti_verify'),
    path('cod/initiate/', views.cod_initiate, name='cod_initiate'),
    path('payment/success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('payment/failure/<int:payment_id>/', views.payment_failure, name='payment_failure'),
    path('payment/cancel/<int:payment_id>/', views.payment_cancel, name='payment_cancel'),
]
