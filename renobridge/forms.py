from django import forms
from .models import Contractor, Homeowner, CollaborationRequest

class ContractorProfileForm(forms.ModelForm):
    class Meta:
        model = Contractor
        fields = ['company_name', 'company_address', 'email_address', 'years_of_experience', 'description', 'logo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class HomeownerForm(forms.ModelForm):
    class Meta:
        model = Homeowner
        fields = ['full_name', 'location', 'property_type', 'property_size', 'preferred_style', 'services_required', 'budget', 'duration', 'floorplan_img']
        widgets = {
            'services_required': forms.Textarea(attrs={'rows': 3}),
        }

class ProposalForm(forms.ModelForm):
    class Meta:
        model = CollaborationRequest
        fields = ['suggested_cost', 'suggested_duration', 'suggested_start_date']
        widgets = {
            'suggested_start_date': forms.SelectDateWidget()
        }