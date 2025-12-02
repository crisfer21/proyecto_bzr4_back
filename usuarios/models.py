from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')

    def __str__(self):
        return self.username