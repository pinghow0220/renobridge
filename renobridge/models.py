from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=20)  # Store userType (e.g., "homeowner", "contractor")

    def __str__(self):
        return self.username

class Homeowner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    property_type = models.CharField(max_length=100)
    property_size = models.CharField(max_length=100)
    preferred_style = models.CharField(max_length=100)
    services_required = models.TextField()  # Store services as comma-separated values
    budget = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)

class Contractor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    company_address = models.CharField(max_length=200)
    email_address = models.EmailField()
    years_of_experience = models.CharField(max_length=50)
    description = models.TextField()
    preferred_location = models.CharField(max_length=100)
    services_provided = models.TextField()  # Store services as comma-separated values
    expertise_styles = models.TextField()  # Store expertise styles as comma-separated values

class ProjectPhoto(models.Model):
    contractor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='project_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)