

from django.urls import path
from .views import (
    CartView, 
    AddToCartView, 
    SendOTPView, 
    UpdateCartItemView, 
    RemoveCartItemView,
    ApplyCouponView,
    CheckoutView,
    PlaceOrderView
)

urlpatterns = [
    path('', CartView.as_view()),
    path('add/', AddToCartView.as_view()),
    path('update/<int:item_id>/', UpdateCartItemView.as_view()),
    path('remove/<int:item_id>/', RemoveCartItemView.as_view()),
    path('checkout/', CheckoutView.as_view()),
    path('place-order/', PlaceOrderView.as_view(), name='place-order'),
    path('apply-coupon/', ApplyCouponView.as_view()),
    path('send-otp/', SendOTPView.as_view()),
]