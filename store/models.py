import uuid
from django.db import models
from authentication.models import User
from .utils import validate_uz_phone_number

TAKING_TYPE = (
    (0, '---'),
    (1, 'topshirish punkti'),
    (2, 'kurier orqali eshikacha')
)

CATEGORY_CHOICES = (
    (1, 'MEN'),
    (2, 'WOMEN'),
    (3, 'BABY')
)

PAYMENT_TYPE = (
    (0, '---'),
    (1, 'CASH'),
    (2, 'PAYME')
)

ORDER_STATUS = (
    (0, 'CANCELED'),
    (1, 'PENDING'),
    (2, 'IN PROCESS'),
    (3, 'DELIVERED')
)

PAYMENT_STATUS = (
    (0, '---'),
    (1, 'PENDING'),
    (2, 'PAYED')
)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class Brand(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Color(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Size(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Genre(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Promocode(BaseModel):
    name = models.CharField(max_length=255)
    discount = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class PromoCodeObj(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    promo = models.ForeignKey(Promocode, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.user)


class Product(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    category = models.PositiveIntegerField(choices=CATEGORY_CHOICES, default=1)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)

    color = models.ForeignKey(Color, on_delete=models.CASCADE, blank=True, null=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, blank=True, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, blank=True, null=True)
    product_quantity = models.PositiveIntegerField(default=0)

    price = models.FloatField(default=0)
    discount = models.IntegerField(default=0)
    price_with_discount = models.DecimalField(default=0, max_digits=13, decimal_places=2)

    rating = models.FloatField(default=0)
    rating_count = models.PositiveIntegerField(default=0)
    object = None

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.price_with_discount = self.price - ((self.discount / 100) * self.price)
        return super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return self.name


class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ManyToManyField(Product, null=True)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.FloatField(default=0)
    delivery_address = models.CharField(max_length=200, blank=True)
    taking_type = models.IntegerField(choices=TAKING_TYPE, default=0)
    delivery_point = models.CharField(max_length=200, blank=True)
    first_name = models.CharField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=13, validators=[validate_uz_phone_number])
    payment_type = models.IntegerField(choices=PAYMENT_TYPE, default=0)
    payment_status = models.IntegerField(choices=PAYMENT_STATUS, default=1)
    status = models.IntegerField(choices=ORDER_STATUS, default=1)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    promo = models.ForeignKey(Promocode, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.last_name}"


class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    price = models.FloatField(default=0)
    discount = models.IntegerField(default=0)
    price_with_discount = models.FloatField(default=0)
    quantity = models.PositiveIntegerField(default=0)
    total_price_with_discount = models.DecimalField(default=0, max_digits=13, decimal_places=2)
    total_price_without_discount = models.DecimalField(default=0, max_digits=13, decimal_places=2)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Like(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.product.name


class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_comment')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    message = models.TextField()
    rating = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.message
