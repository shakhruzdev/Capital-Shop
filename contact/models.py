from django.db import models
from store.models import BaseModel


class Contact(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    message = models.TextField()

    is_solved = models.BooleanField(default=False)

    def __str__(self):
        return self.email
