from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .models import CustomUser  # Ensure you have a custom user model
from django.contrib.auth.views import LoginView
from .models import Homeowner, Contractor, ProjectPhoto, CollaborationRequest, Project, Expense
from django.shortcuts import get_object_or_404
from .forms import ContractorProfileForm, HomeownerForm, ProposalForm, ProcessSelectionForm, ExpenseForm
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseForbidden
from django import forms
from collections import defaultdict
from decimal import Decimal
from django.template.loader import get_template
from xhtml2pdf import pisa



def renobridge(request):
    return render(request, 'index.html')

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
    contractor = get_object_or_404(Contractor, user__id=id)

    # Fetch all uploaded photos by the contractor
    project_photos = ProjectPhoto.objects.filter(contractor=contractor)
    print(f"Photos count: {project_photos.count()}")
    
    context = {
        'contractor': contractor,
        'project_photos': project_photos
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
        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            project_photo = ProjectPhoto(contractor=contractor, photo=photo)
            project_photo.save()
            return redirect('expert_profile', id=id)

    # Fetch all uploaded photos by the contractor
    project_photos = ProjectPhoto.objects.filter(contractor=contractor)
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

        # Check if a contractor instance already exists
        contractor_exists = Contractor.objects.filter(user=request.user).exists()

        if not contractor_exists:
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
        else:
            return render(request, 'experts_input.html', {'error': 'Contractor profile already exists.'})

    return render(request, 'experts_input.html')


def completion_page(request):
    return render(request, 'completion_page.html')

def myfirst(request):
    return render(request, 'myfirst.html')

def owner_confirmation_list(request):
    return render(request, 'owner_confirmation_list.html')


def owner_input(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullName', '')
        location = request.POST.get('location', '')
        property_type = request.POST.get('propertyType', '')
        property_size = request.POST.get('propertySize', '')
        preferred_style = request.POST.get('preferredStyle', '')
        services_required = ','.join(request.POST.getlist('services'))
        budget = request.POST.get('budget', '')
        duration = request.POST.get('duration', '')
        start_date = request.POST.get('start_date', '')
        floorplan_img = request.FILES.get('floorplan_img', None)

        # Check that all fields are not empty
        if not (full_name and location and property_type and property_size and preferred_style and start_date):
            return render(request, 'owner_input.html', {
                'error': 'All fields are required.'
            })

        # Save homeowner details
        try:
            homeowner, created = Homeowner.objects.get_or_create(user=request.user)

            # Update homeowner fields
            homeowner.full_name = full_name
            homeowner.location = location
            homeowner.property_type = property_type
            homeowner.property_size = property_size
            homeowner.preferred_style = preferred_style
            homeowner.services_required = services_required
            homeowner.budget = budget
            homeowner.duration = duration
            homeowner.start_date = start_date
            if floorplan_img:
                homeowner.floorplan_img = floorplan_img

            homeowner.save()
            return redirect('expert_list')

        except Exception as e:
            return render(request, 'owner_input.html', {
                'error': f'Error saving data: {str(e)}'
            })

    else:
        try:
            homeowner = Homeowner.objects.get(user=request.user)
            return render(request, 'owner_input.html', {
                'homeowner': homeowner,
            })
        except Homeowner.DoesNotExist:
            return render(request, 'owner_input.html')

    return render(request, 'owner_input.html')


def expert_invitation_list(request):
    contractor = request.user.contractor
    invitations = CollaborationRequest.objects.filter(contractor=contractor, status="Pending")

    return render(request, 'expert_invitation_list.html', {'invitations': invitations})

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

def request_collaboration(request, contractor_id):
    if request.method == 'POST':
        # Get the contractor instance or return 404 if it does not exist
        contractor = get_object_or_404(Contractor, id=contractor_id)
        
        # Get the homeowner associated with the current user
        homeowner = get_object_or_404(Homeowner, user=request.user)

        # Create collaboration request
        collaboration_request = CollaborationRequest.objects.create(
            homeowner=homeowner,
            contractor=contractor,
            status="Pending"
        )

        # Notify contractor via email
        send_mail(
            subject='New Collaboration Request',
            message=f'Hello {contractor.company_name}, you have received a new collaboration request from {homeowner.full_name}.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contractor.email_address]
        )

    return redirect('expert_list')

def suggest_proposal(request, invitation_id):
    if request.method == 'POST':
        # Get the invitation instance or return 404 if it does not exist
        invitation = get_object_or_404(CollaborationRequest, id=invitation_id)

        # Make sure the current user is the contractor for this invitation
        if invitation.contractor.user != request.user:
            return HttpResponseForbidden()

        # Update the status of the invitation to "Proposal Suggested"
        invitation.status = "Proposal Suggested"
        invitation.save()

        # Redirect to the expert invitation list
        return redirect('expert_invitation_list')

    return redirect('expert_dashboard')

def reject_proposal(request, invitation_id):
    if request.method == 'POST':
        # Get the invitation instance or return 404 if it does not exist
        invitation = get_object_or_404(CollaborationRequest, id=invitation_id)

        # Make sure the current user is the contractor for this invitation
        if invitation.contractor.user != request.user:
            return HttpResponseForbidden()

        # Update the status of the invitation to "Rejected"
        invitation.status = "Rejected"
        invitation.save()

        # Redirect to the expert invitation list
        return redirect('expert_invitation_list')

    return redirect('expert_dashboard')

def suggest_proposal(request, invitation_id):
    # Fetch the collaboration request using the provided ID
    invitation = get_object_or_404(CollaborationRequest, id=invitation_id)

    if request.method == 'POST':
        # Get the suggested details from the contractor's input
        suggested_cost = request.POST.get('suggested_cost')
        suggested_duration = request.POST.get('suggested_duration')
        suggested_start_date = request.POST.get('suggested_start_date')

        # Save the suggested proposal details to the CollaborationRequest
        invitation.suggested_cost = suggested_cost
        invitation.suggested_duration = suggested_duration
        invitation.suggested_start_date = suggested_start_date
        invitation.status = "Proposal Sent"  # Update the status to match the homeowner's view
        invitation.save()

        # Send notification email to the homeowner
        send_mail(
            subject='New Proposal Received',
            message=f'Hello {invitation.homeowner.full_name},\n\n'
                    f'{invitation.contractor.company_name} has submitted a proposal for your project:\n'
                    f'Cost: {suggested_cost}\n'
                    f'Duration: {suggested_duration} days\n'
                    f'Start Date: {suggested_start_date}\n\n'
                    f'Please log in to view more details.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.homeowner.user.email],
            fail_silently=False,
        )

        # Redirect back to the invitation list after saving the proposal
        return redirect('expert_invitation_list')

    return render(request, 'suggest_proposal.html', {'invitation': invitation})


def compare_proposals(request):
    homeowner = Homeowner.objects.get(user=request.user)
    proposals = CollaborationRequest.objects.filter(homeowner=homeowner, status="Proposal Sent")

    print(f"Fetched Proposals Count: {proposals.count()}")
    
    context = {
        'proposals': proposals
    }
    return render(request, 'compare_proposals.html', context)

def start_project(request, proposal_id):
    if request.method == 'POST':
        collaboration_request = get_object_or_404(CollaborationRequest, id=proposal_id)

        collaboration_request.status = "In Progress"
        collaboration_request.save()

        contractor = collaboration_request.contractor
        # Ensure this contractor exists in the system and matches the one who logs in later.
        if not Contractor.objects.filter(pk=contractor.pk).exists():
            return redirect('dashboard')  # Handle error or redirect accordingly

        # Create project with validated contractor
        project = Project.objects.create(
            owner=collaboration_request.homeowner,
            contractor=contractor,
            budget_allocated=collaboration_request.suggested_cost,
            total_duration=collaboration_request.suggested_duration
        )
        project.save()

        print(f'Project created: ID={project.id}, Owner={project.owner}, Contractor={project.contractor}')

        # Notify contractor via email
        send_mail(
            subject='Collaboration Request Accepted',
            message=f'Hello {contractor.company_name},\n\n'
                    f'The homeowner has accepted your proposal for the project starting on {collaboration_request.suggested_start_date}.\n\n'
                    f'Please log in to view more details.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contractor.email_address],
            fail_silently=False,
        )

        return redirect('dashboard')

    return redirect('compare_proposals')


@login_required
def contractor_dashboard(request):
    contractor = get_object_or_404(Contractor, user=request.user)
    ongoing_projects = Project.objects.filter(contractor=contractor)
    print(f'contractor_dashboard view reached for contractor: {contractor.company_name}')
    print(f'Ongoing projects for contractor {contractor.company_name}: {list(ongoing_projects)}')
    return render(request, 'expert_dashboard.html', {'projects': ongoing_projects})

@login_required
def select_processes(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        # Extract custom processes from POST data
        custom_processes = request.POST.getlist('processes_required')

        # Create a new instance of the form with POST data
        form = ProcessSelectionForm(request.POST)

        # Add custom processes to the choices before form validation
        current_choices = form.fields['processes_required'].choices
        updated_choices = current_choices + [(custom, custom) for custom in custom_processes if custom not in dict(current_choices)]
        form.fields['processes_required'].choices = updated_choices

        if form.is_valid():
            # Save selected processes to the project
            project.processes_required = form.cleaned_data['processes_required']
            project.save()
            return redirect('update_progress', project_id=project.id)

    else:
        form = ProcessSelectionForm()

    return render(request, 'select_processes.html', {'form': form, 'project': project})

@login_required
def update_progress(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # Extract the required processes list
    processes_required = project.processes_required if project.processes_required else []

    # Define a dynamic form for selecting completed tasks based on required processes
    class ProgressUpdateForm(forms.Form):
        processes_completed = forms.MultipleChoiceField(
            choices=[(process, process.replace('_', ' ').title()) for process in processes_required],
            widget=forms.CheckboxSelectMultiple,
            required=False
        )

    # Handle the form submission
    if request.method == 'POST':
        form = ProgressUpdateForm(request.POST)
        if form.is_valid():
            # Update the processes completed
            project.processes_completed = form.cleaned_data['processes_completed']
            
            # Calculate progress percentage
            total_tasks = len(processes_required)
            completed_tasks = len(project.processes_completed) if project.processes_completed else 0
            project.progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

            # Save the updated project details
            project.save()

            # Redirect to contractor dashboard or a summary page
            return redirect('expert_dashboard')

    # If request is not POST, render the form with initial data
    else:
        initial_data = {'processes_completed': project.processes_completed}
        form = ProgressUpdateForm(initial=initial_data)

    return render(request, 'update_progress.html', {'form': form, 'project': project})

@login_required
def upload_project_photo(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    contractor = get_object_or_404(Contractor, user=request.user)

    if request.method == 'POST' and request.FILES.get('progress_photo'):
        photo = request.FILES['progress_photo']
        ProjectPhoto.objects.create(project=project, contractor=contractor, photo=photo)
        return redirect('expert_dashboard')

    return redirect('expert_dashboard')

@login_required
def view_project_photos(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    return render(request, 'view_project_photos.html', {'project': project})

# View for contractors to update expenses
def update_expense(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.project = project
            expense.save()
            # Update the project's expenses spent
            project.expenses_spent += expense.amount
            project.save()
            return redirect('expert_dashboard')  # Redirect to a relevant page

    else:
        form = ExpenseForm()
    
    return render(request, 'update_expense.html', {'form': form, 'project': project})

# View for homeowners to see expenses
def view_expenses(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    expenses = project.expenses.all()
    budget_remaining = project.budget_allocated - project.expenses_spent if project.budget_allocated and project.expenses_spent else None
    
    return render(request, 'view_expenses.html',{
        'project': project,
        'expenses': expenses,
        'budget_remaining': budget_remaining
    })

@login_required
def dashboard(request):
    homeowner = get_object_or_404(Homeowner, user=request.user)
    project = Project.objects.filter(owner=homeowner).first()

    if project:
        expenses = project.expenses.all()

        # Categorize expenses
        categorized_expenses = defaultdict(float)
        for expense in expenses:
            categorized_expenses[expense.category] += float(expense.amount)

        remaining_duration = max(project.total_duration - project.duration_spent, 0)

        # Redirect to completion page if progress is 100%
        if project.progress_percentage >= 100:
            return redirect('completion_page', project_id=project.id)

    else:
        categorized_expenses = {}
        remaining_duration = 0

    categorized_expenses = dict(categorized_expenses)

    context = {
        'project': project,
        'categorized_expenses': categorized_expenses,
        'remaining_duration': remaining_duration,
    }

    return render(request, 'dashboard.html', context)

@login_required
def completion_page(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'completion_page.html', {'project': project})

def download_invoice(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    template_path = 'invoice_template.html'
    context = {'project': project, 'expenses': project.expenses.all()}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_project_{project.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response