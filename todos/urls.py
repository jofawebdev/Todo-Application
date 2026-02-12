"""
URL routing for the Todo application.

Following REST-style conventions:
- List view: GET /
- Create: POST /create/ (form at GET /create/)
- Update: POST /update/<pk>/ (form at GET /update/<pk>/)
- Delete: POST /delete/<pk>/ (confirmation at GET /delete/<pk>/)
- Action: POST /toggle/<pk>/ (no template, redirects immediately)
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    RegisterView, 
    LoginView, 
    logout_view,
    profile
)
from django.conf import settings
from django.conf.urls.static import static

app_name = 'todos'  # For namespacing URLs

urlpatterns = [
    # List all todos (homepage)
    path('', views.TodoListView.as_view(), name='todo_list'),
    
    # Create new todo
    path('create/', views.TodoCreateView.as_view(), name='todo_create'),
    
    # Update existing todo
    path('update/<int:pk>/', views.TodoUpdateView.as_view(), name='todo_update'),
    
    # Delete todo (with confirmation)
    path('delete/<int:pk>/', views.TodoDeleteView.as_view(), name='todo_delete'),
    
    # Toggle completion status
    path('toggle/<int:pk>/', views.toggle_completion, name='todo_toggle'),
    
    # User Authentication URLs
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    
    # User Profile
    path('profile/', profile, name='profile'),
    
    # Password Reset URLs (Django built-in views)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)