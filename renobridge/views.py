from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .models import CustomUser  # Ensure you have a custom user model
from django.contrib.auth.views import LoginView
from .models import Homeowner, Contractor, ProjectPhoto
from django.shortcuts import get_object_or_404
from .forms import ContractorProfileForm, HomeownerForm


def renobridge(request):
    return render(request, 'index.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def expert_list(request):
    try:
        # Assuming the logged-in user is a homeowner
        homeowner = Homeowner.objects.get(user=request.user)

        # Find matching contractors
        matching_contractors = Contractor.objects.filter(
            preferred_location=homeowner.location,
            expertise_styles__icontains=homeowner.preferred_style,
            services_provided__icontains=homeowner.services_required
        )

        context = {
            'matching_contractors': matching_contractors
        }
        return render(request, 'expert_list.html', context)

    except Homeowner.DoesNotExist:
        return render(request, 'expert_list.html', {
            'error': 'Homeowner data does not exist for the current user. Please fill out the homeowner form.'
        })

def expert_portfolio(request, id):
    # Get the CustomUser instance using the provided id
    user = get_object_or_404(CustomUser, id=id)
    
    # Get the corresponding Contractor instance using the user
    contractor = get_object_or_404(Contractor, user=user)

    # Fetch all uploaded photos by the contractor
    project_photos = ProjectPhoto.objects.filter(contractor=user)  # use the user to query the contractor field in ProjectPhoto

    context = {
        'contractor': contractor,
        'project_photos': project_photos,
    }
    return render(request, 'expert_portfolio.html', context)

def expert_profile(request, id):
    contractor = get_object_or_404(Contractor, user__id=id)

    if request.method == 'POST':
        # Handle company logo upload
        if 'logo' in request.FILES:
            contractor.logo = request.FILES['logo']
            contractor.save()
            return redirect('expert_profile', id=id)
        
        # Handle project photo upload
        if 'project_photo' in request.FILES:
            photo = request.FILES['project_photo']
            project_photo = ProjectPhoto(contractor=contractor.user, photo=photo)
            project_photo.save()
            return redirect('expert_profile', id=id)

    # Fetch all uploaded photos by the contractor
    project_photos = ProjectPhoto.objects.filter(contractor=request.user)
    print(f"Photos count: {project_photos.count()}")
    
    context = {
        'contractor': contractor,
        'project_photos': project_photos
    }
    return render(request, 'expert_profile.html', context)

def experts_input(request):
    if request.method == 'POST':
        company_name = request.POST['companyName']
        company_address = request.POST['companyAddress']
        email = request.POST['email']
        years_of_experience = request.POST['yearsOfExperience']
        description = request.POST['description']
        preferred_location = request.POST['location']
        services_provided = ','.join(request.POST.getlist('services'))
        expertise_styles = ','.join(request.POST.getlist('expertise_styles'))

        # Save contractor details
        contractor = Contractor.objects.create(
            user=request.user,
            company_name=company_name,
            company_address=company_address,
            email_address=email,
            years_of_experience=years_of_experience,
            description=description,
            preferred_location=preferred_location,
            services_provided=services_provided,
            expertise_styles=expertise_styles
        )
        contractor.save()
        return redirect('expert_profile', id=contractor.user.id)
    return render(request, 'experts_input.html')


def completion_page(request):
    return render(request, 'completion_page.html')

def myfirst(request):
    return render(request, 'myfirst.html')

def owner_confirmation_list(request):
    return render(request, 'owner_confirmation_list.html')


def owner_input(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullName','')
        location = request.POST.get('location', '')
        property_type = request.POST.get('propertyType', '')
        property_size = request.POST.get('propertySize', '')
        preferred_style = request.POST.get('preferredStyle', '')
        services_required = ','.join(request.POST.getlist('services'))
        budget = request.POST.get('budget', '')
        duration = request.POST.get('duration', '')
        floorplan_img = request.FILES.get('floorplan_img', None)
        # Check that all fields are not empty
        if not (full_name and location and property_type and property_size and preferred_style):
            return render(request, 'owner_input.html', {
                'error': 'All fields are required.'
            })

        # Save homeowner details
        try:
            homeowner = Homeowner.objects.create(
                user=request.user,
                full_name=full_name,
                location=location,
                property_type=property_type,
                property_size=property_size,
                preferred_style=preferred_style,
                services_required=services_required,
                budget=budget,
                duration=duration,
                floorplan_img=floorplan_img
            )
            homeowner.save()
            return redirect('expert_list')
        except Exception as e:
            return render(request, 'owner_input.html', {
                'error': f'Error saving data: {str(e)}'
            })

    return render(request, 'owner_input.html')

def expert_invitation_list(request):
    return render(request, 'expert_invitation_list.html')

def expert_dashboard(request):
    return render(request, 'expert_dashboard.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST['userType']  # Homeowner or Contractor

        if password != confirm_password:
            # If passwords do not match, return an error message
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        # Create user
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        user.user_type = user_type  # Set user_type
        user.save()

        # Log the user in
        auth_login(request, user)

        # Redirect based on user type
        if user_type == 'homeowner':
            return redirect('owner_input')
        elif user_type == 'contractor':
            return redirect('experts_input')
    else:
        return render(request, 'register.html')

    
class CustomLoginView(LoginView):
    def form_valid(self, form):
        # Log the user in
        auth_login(self.request, form.get_user())
        
        # Redirect based on user type
        user_type = form.get_user().user_type
        if user_type == 'homeowner':
            return redirect('dashboard')
        elif user_type == 'contractor':
            return redirect('expert_dashboard')
        return super().form_valid(form)

@login_required
def edit_contractor_profile(request, id):
    contractor = get_object_or_404(Contractor, user__id=id)
    
    if request.method == 'POST':
        form = ContractorProfileForm(request.POST, request.FILES, instance=contractor)
        if form.is_valid():
            form.save()
            return redirect('expert_profile', id=id)
    else:
        form = ContractorProfileForm(instance=contractor)

    context = {
        'form': form,
        'contractor': contractor
    }
    return render(request, 'edit_contractor_profile.html', context)

@login_required
def view_homeowner_input(request):
    homeowner = get_object_or_404(Homeowner, user=request.user)
    context = {
        'homeowner': homeowner
    }
    return render(request, 'view_homeowner_input.html', context)

@login_required
def edit_homeowner_input(request):
    homeowner = get_object_or_404(Homeowner, user=request.user)

    if request.method == 'POST':
        form = HomeownerForm(request.POST, request.FILES, instance=homeowner)
        if form.is_valid():
            form.save()
            return redirect('view_homeowner_input')
    else:
        form = HomeownerForm(instance=homeowner)

    return render(request, 'edit_homeowner_input.html', {'form': form})