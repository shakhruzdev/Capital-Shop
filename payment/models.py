from django.db import models
from store.models import BaseModel
from authentication.models import User
from authentication.utils import validate_uz_phone_number

BANK_CHOICES = (
    (1, 'IPOTEKABANK'),
    (2, 'QQBBANK'),
    (3, 'ORIENTFINANSBANK'),
    (4, 'KAPITALBANK'),
    (5, 'ASIAALLIANCEBANK'),
)

CARD_CHOICES = (
    (1, 'VISA'),
    (2, 'MASTERCARD'),
    (3, 'UZCARD'),
    (4, 'HUMO')
)


class Card(BaseModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=13, validators=[validate_uz_phone_number], null=True)
    pan = models.IntegerField()
    cvv = models.CharField(max_length=3, blank=True)
    bank_name = models.PositiveIntegerField(choices=BANK_CHOICES)
    card_name = models.PositiveIntegerField(choices=CARD_CHOICES)
    balance = models.PositiveIntegerField(default=0)
    created_month = models.IntegerField()
    created_year = models.IntegerField()
    expired_month = models.IntegerField(default=0)
    expired_year = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class UserCard(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=13, validators=[validate_uz_phone_number], null=True)
    pan = models.IntegerField()
    cvv = models.CharField(max_length=3, blank=True)
    bank_name = models.PositiveIntegerField(choices=BANK_CHOICES)
    card_name = models.PositiveIntegerField(choices=CARD_CHOICES)
    balance = models.PositiveIntegerField(default=0)
    created_month = models.IntegerField()
    created_year = models.IntegerField()
    expired_month = models.IntegerField(default=0)
    expired_year = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
