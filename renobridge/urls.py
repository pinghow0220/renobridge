from django.urls import path
from . import views
from .views import CustomLoginView 
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('renobridge/', views.renobridge, name='renobridge'),  
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('tips01/', views.tips01, name='tips01'),
    path('tips02/', views.tips02, name='tips02'),
    path('tips03/', views.tips03, name='tips03'),
    path('about_us/', views.about_us, name='about_us'),
    path('view_homeowner_input/', views.view_homeowner_input, name='view_homeowner_input'),
    path('edit_homeowner_input/', views.edit_homeowner_input, name='edit_homeowner_input'),
    path('expert_list/', views.expert_list, name='expert_list'),  
    path('expert_portfolio/<int:id>', views.expert_portfolio, name='expert_portfolio'), 
    path('expert_profile/<int:id>/', views.expert_profile, name='expert_profile'), 
    path('edit_contractor_profile/<int:id>/', views.edit_contractor_profile, name='edit_contractor_profile'),
    path('experts_input/', views.experts_input, name='experts_input'),  
    path('completion_page/<int:project_id>/', views.completion_page, name='completion_page'),
   
    path('myfirst/', views.myfirst, name='myfirst'),  
    path('owner_confirmation_list/', views.owner_confirmation_list, name='owner_confirmation_list'),  
    path('owner_input/', views.owner_input, name='owner_input'),  
    path('register/', views.register, name='register'),  
    path('expert_invitation_list/',views.expert_invitation_list, name='expert_invitation_list'),
    path('expert_dashboard/', views.expert_dashboard, name='expert_dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('request_collaboration/<int:contractor_id>/', views.request_collaboration, name='request_collaboration'),
    path('suggest_proposal/<int:invitation_id>/', views.suggest_proposal, name='suggest_proposal'),
    path('reject_proposal/<int:invitation_id>/', views.reject_proposal, name='reject_proposal'),
    path('suggest_proposal/<int:invitation_id>/', views.suggest_proposal, name='suggest_proposal'),
    path('compare_proposals/', views.compare_proposals, name='compare_proposals'),
    path('start_project/<int:proposal_id>/', views.start_project, name='start_project'),
    path('expert/dashboard/', views.contractor_dashboard, name='expert_dashboard'),
    path('project/<int:project_id>/select_processes/', views.select_processes, name='select_processes'),
    path('project/<int:project_id>/update_progress/', views.update_progress, name='update_progress'),
    path('project/<int:project_id>/upload_photo/', views.upload_project_photo, name='upload_project_photo'),
    path('project/<int:project_id>/photos/', views.view_project_photos, name='view_project_photos'),
    path('project/<int:project_id>/update_expense/', views.update_expense, name='update_expense'),
    path('project/<int:project_id>/expenses/', views.view_expenses, name='view_expenses'),
    path('download_invoice/<int:project_id>/', views.download_invoice, name='download_invoice'),
    path('submit_review/<int:project_id>/', views.submit_review, name='submit_review'),
    path('project/<int:project_id>/expense/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    path('project/<int:project_id>/details/', views.project_details, name='project_details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
