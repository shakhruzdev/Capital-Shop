from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from .utils import validate_uz_phone_number

GENDER_CHOICE = (
    (1, '---'),
    (2, 'MALE'),
    (3, 'FEMALE')
)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='user/images/', default='user/images/default_user.png')
    phone_number = models.CharField(max_length=13, unique=True, validators=[validate_uz_phone_number], null=True)
    username = None
    gender = models.PositiveIntegerField(choices=GENDER_CHOICE, default=1)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
