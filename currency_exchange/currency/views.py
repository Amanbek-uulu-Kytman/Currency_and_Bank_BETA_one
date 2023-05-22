from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.
# currency/views.py
import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer


# currency/views.py

import pyotp
from django.core.mail import send_mail
from django.conf import settings


# currency/views.py

from django.contrib.auth.models import User
from .models import Account

class UserRegistrationView(APIView):
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            passport_id = serializer.validated_data['passport_id']
            invest_sum = serializer.validated_data['invest_sum']

            # Создание пользователя
            user = User.objects.create_user(username=username, email=email, password=password)

            # Открытие счетов
            currencies = ['USD', 'EUR', 'RUB', 'KGS']
            for currency in currencies:
                account = Account.objects.create(user=user, currency=currency)
                if currency == 'KGS':
                    account.balance = invest_sum
                    account.save()

            # Генерация и сохранение PIN-кода
            totp = pyotp.TOTP(user.email)
            pin_code = totp.now()
            user.pin_code = pin_code
            user.is_active = False
            user.save()

            # Отправка письма с PIN-кодом
            message = f"Your one-time PIN code is: {pin_code}"
            send_mail(
                'Confirmation PIN code',
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return Response({'message': 'Registration successful. Please check your email for the PIN code.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# currency/views.py

class OTPVerificationView(APIView):
    def post(self, request, format=None):
        pin_code = request.data.get('pin')
        username = request.data.get('username')

        try:
            user = User.objects.get(username=username)
            totp = pyotp.TOTP(user.email)
            if totp.verify(pin_code):
                user.is_active = True  # Активация учетной записи
                user.save()
                return Response({'message': 'OTP verification successful. Your account has been activated.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            pass

        return Response({'message': 'Invalid OTP or username'}, status=status.HTTP_400_BAD_REQUEST)
# currency/views.py



@method_decorator(login_required, name='dispatch')
class CurrencyExchangeView(APIView):
    def post(self, request, format=None):
        from_currency = request.data.get('from')
        amount = request.data.get('amount')
        to_currency = request.data.get('to')

        # Логика обмена валюты
        # Ваш код обмена валюты здесь

        return Response({'message': 'Currency exchange successful'}, status=status.HTTP_200_OK)


# currency/views.py



# Ваш код для получения данных API с курсами валют
def get_exchange_rate(from_currency, to_currency):
    url = f"https://api.fawazahmed0.me/currency/{from_currency}/{to_currency}"
    response = requests.get(url)
    data = response.json()
    exchange_rate = data['rate']
    return exchange_rate

@method_decorator(login_required, name='dispatch')
class CurrencyExchangeView(APIView):
    def post(self, request, format=None):
        from_currency = request.data.get('from')
        amount = float(request.data.get('amount'))
        to_currency = request.data.get('to')

        # Получение типа пользователя и расчет комиссии
        user = request.user
        user_type = user.profile.user_type

        if user_type == 'citizen_kr':
            commission = 0
        elif user_type == 'citizen_other':
            commission = 0.01
        elif user_type == 'vip':
            commission = 0.007
        else:
            return Response({'message': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

        # Расчет комиссии и суммы после комиссии
        commission_amount = amount * commission
        exchanged_amount = amount - commission_amount

        # Получение курса валют с использованием API
        exchange_rate = get_exchange_rate(from_currency, to_currency)

        # Вычисление суммы валюты для обмена
        exchanged_currency_amount = exchanged_amount / exchange_rate

        # Обновление баланса счетов
        try:
            from_account = Account.objects.get(user=user, currency=from_currency)
            to_account = Account.objects.get(user=user, currency=to_currency)
        except Account.DoesNotExist:
            return Response({'message': 'Invalid account currency'}, status=status.HTTP_400_BAD_REQUEST)

        if from_account.balance < amount:
            return Response({'message': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        from_account.balance -= amount
        to_account.balance += exchanged_currency_amount
        from_account.save()
        to_account.save()

        return Response({'message': 'Currency exchange successful'}, status=status.HTTP_200_OK)

# currency/views.py

from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Account, CompanyAccount

@method_decorator(login_required, name='dispatch')
class CurrencyExchangeView(APIView):
    def post(self, request, format=None):
        # ... ваш код для проверки типа пользователя, расчета комиссии и обмена валюты ...

        # Обновление баланса счетов
        try:
            from_account = Account.objects.get(user=user, currency=from_currency)
            to_account = Account.objects.get(user=user, currency=to_currency)
            company_account = CompanyAccount.objects.get(currency=from_currency)
        except (Account.DoesNotExist, CompanyAccount.DoesNotExist):
            return Response({'message': 'Invalid account currency'}, status=status.HTTP_400_BAD_REQUEST)

        if from_account.balance < amount:
            return Response({'message': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        from_account.balance -= amount
        to_account.balance += exchanged_currency_amount
        company_account.balance += commission_amount

        from_account.save()
        to_account.save()
        company_account.save()

        return Response({'message': 'Currency exchange successful'}, status=status.HTTP_200_OK)

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class CompanyAccountsView(APIView):
    def get(self, request, format=None):
        company_accounts = CompanyAccount.objects.all()
        accounts_data = {account.currency: account.balance for account in company_accounts}
        return Response(accounts_data, status=status.HTTP_200_OK)
