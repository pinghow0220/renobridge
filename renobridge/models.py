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
    full_address = models.TextField(max_length=400)
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
    average_rating = models.FloatField(default=0.0)

class ProjectPhoto(models.Model):
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True, related_name='photos')
    photo = models.ImageField(upload_to='project_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Photo for Contractor {self.contractor.user.username}'
    
class ProgressPhoto(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='progress_photos')
    photo = models.ImageField(upload_to='progress_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Progress Photo for Project {self.project.id}'

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
    
class Project(models.Model):
    owner = models.ForeignKey(Homeowner, on_delete=models.CASCADE, related_name='projects')
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True, related_name='projects')
    processes_required = models.JSONField(null=True, blank=True)
    processes_completed = models.JSONField(null=True, blank=True)
    budget_allocated = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expenses_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_duration = models.PositiveIntegerField(help_text="Expected total duration in days", null=True, blank=True)
    duration_spent = models.PositiveIntegerField(help_text="Actual duration spent in days", default=0)
    progress_percentage = models.FloatField(default=0)
    status = models.CharField(max_length=20, default='In Progress')


    def __str__(self):
        return f'Project for {self.owner.user.username} - {self.id}'

class Expense(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='expenses')
    item = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.item} - {self.amount}'

@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'homeowner':
            Homeowner.objects.create(user=instance)
        elif instance.user_type == 'contractor':
            Contractor.objects.create(user=instance)

class Review(models.Model):
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='reviews')
    homeowner = models.ForeignKey(Homeowner, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)