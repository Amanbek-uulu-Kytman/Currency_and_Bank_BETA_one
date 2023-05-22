# currency/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    passport_id = serializers.CharField()
    invest_sum = serializers.IntegerField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'passport_id', 'invest_sum')

    def create(self, validated_data):
        password = validated_data.pop('password')
        passport_id = validated_data.pop('passport_id')
        invest_sum = validated_data.pop('invest_sum')
        user = User(**validated_data)
        user.set_password(password)

        # Определение типа пользователя на основе суммы пополнения счета
        if invest_sum >= 1000000:
            user.user_type = 'VIP'
        elif user.passport_id == 'КР':
            user.user_type = 'Citizen'
        else:
            user.user_type = 'Foreign'

        user.save()
        return user
