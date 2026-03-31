# accounts/urls.py
from django.urls import path


from .views import RegisterView, SendOTPView, VerifyOTPView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('send-otp/', SendOTPView.as_view()),
    path('verify-otp/', VerifyOTPView.as_view()),
]