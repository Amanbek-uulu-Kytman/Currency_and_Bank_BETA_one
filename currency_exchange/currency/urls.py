# currency/urls.py

from django.urls import path
from .views import UserRegistrationView, OTPVerificationView, CurrencyExchangeView

urlpatterns = [
    path('api/register/', UserRegistrationView.as_view(), name='register'),
    path('api/otp/', OTPVerificationView.as_view(), name='otp-verification'),
    path('api/change/', CurrencyExchangeView.as_view(), name='currency-exchange'),
]
