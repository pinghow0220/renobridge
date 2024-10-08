from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=20)  # Store userType (e.g., "homeowner", "contractor")

    def __str__(self):
        return self.username

