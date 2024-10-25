from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=20)  # Store userType (e.g., "homeowner", "contractor")

    def __str__(self):
        return self.username

class Homeowner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    property_type = models.CharField(max_length=100)
    property_size = models.CharField(max_length=100)
    preferred_style = models.CharField(max_length=100)
    services_required = models.TextField()  # Store services as comma-separated values
    budget = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    floorplan_img = models.ImageField(upload_to='floorplans/', blank=True, null=True)

class Contractor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    company_address = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    email_address = models.EmailField()
    years_of_experience = models.CharField(max_length=50)
    description = models.TextField()
    preferred_location = models.CharField(max_length=100)
    services_provided = models.TextField()  # Store services as comma-separated values
    expertise_styles = models.TextField()  # Store expertise styles as comma-separated values

class ProjectPhoto(models.Model):
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='project_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class CollaborationRequest(models.Model):
    homeowner = models.ForeignKey(Homeowner, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    # Proposal details
    suggested_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    suggested_duration = models.CharField(max_length=100, null=True, blank=True)
    suggested_start_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Collaboration Request from {self.homeowner.full_name} to {self.contractor.company_name}"

@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'homeowner':
            Homeowner.objects.create(user=instance)
        elif instance.user_type == 'contractor':
            Contractor.objects.create(user=instance)
