from django import forms
from .models import Contractor, Homeowner, CollaborationRequest, Expense

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

class ProcessSelectionForm(forms.Form):
    PROCESSES_CHOICES = [
        ('site_preparation', 'Site Preparation'),
        ('demolition_work', 'Demolition Work'),
        ('debris_removal', 'Debris Removal'),
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('framing', 'Framing'),
        ('structural_changes', 'Structural Changes'),
        ('hvac_installation', 'HVAC Installation'),
        ('insulation_and_drywall', 'Insulation and Drywall'),
        ('flooring_installation', 'Flooring Installation'),
        ('fixtures_and_appliances', 'Fixtures and Appliances'),
        ('painting_and_finishes', 'Painting and Finishes'),
        ('final_inspections', 'Final Inspections'),
    ]
    processes_required = forms.MultipleChoiceField(
        choices=PROCESSES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['item', 'amount', 'category']