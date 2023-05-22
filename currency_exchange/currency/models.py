from django.db import models

# Create your models here.
# currency/models.py

from django.db import models
from django.db import models
from django.contrib.auth.models import User


class CompanyAccount(models.Model):
    currency = models.CharField(max_length=3, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.currency

# currency/models.py



class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - {self.currency}"

