"""
Views for the Todo application.
Fixed delete functionality and added user-based task ownership.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils import timezone
from django.http import Http404
from .models import Todo, Profile
from .forms import TodoForm, RegisterForm, LoginForm, ProfileUpdateForm, UserUpdateForm


class TodoListView(LoginRequiredMixin, ListView):
    """
    Display a list of todos for the logged-in user only.
    """
    model = Todo
    template_name = 'todos/todo_list.html'
    context_object_name = 'todos'
    
    def get_queryset(self):
        """Return only the current user's todos."""
        return Todo.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Add statistics and filter context."""
        context = super().get_context_data(**kwargs)
        
        # Get current user's todos
        user_todos = Todo.objects.filter(user=self.request.user)
        
        # Calculate statistics
        total_count = user_todos.count()
        active_count = user_todos.filter(completed=False).count()
        completed_count = user_todos.filter(completed=True).count()
        overdue_count = sum(1 for todo in user_todos if todo.is_overdue())
        
        # Get filter parameters
        status = self.request.GET.get('status', 'all')
        priority = self.request.GET.get('priority', '')
        
        # Apply filters to queryset
        queryset = user_todos
        if status == 'active':
            queryset = queryset.filter(completed=False)
        elif status == 'completed':
            queryset = queryset.filter(completed=True)
        
        if priority and priority.isdigit():
            queryset = queryset.filter(priority=int(priority))
        
        # Update context
        context.update({
            'todos': queryset,
            'total_count': total_count,
            'active_count': active_count,
            'completed_count': completed_count,
            'overdue_count': overdue_count,
            'current_filter': status,
            'priority_filter': priority,
        })
        
        return context


class TodoCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new todo for the current user.
    """
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('todos:todo_list')
    
    def form_valid(self, form):
        """Set the current user as the todo owner before saving."""
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Task "{self.object.title}" created successfully!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Add page title to context."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create New Task'
        return context


class TodoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing todo (only if user owns it).
    """
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    
    def get_queryset(self):
        """Only allow users to update their own todos."""
        return Todo.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        """Redirect to list view after successful update."""
        return reverse_lazy('todos:todo_list')
    
    def form_valid(self, form):
        """Show success message after update."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Task "{self.object.title}" updated successfully!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        """Add page title to context."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit: {self.object.title}'
        return context


class TodoDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a todo (only if user owns it).
    FIXED: Now properly deletes tasks.
    """
    model = Todo
    template_name = 'todos/todo_confirm_delete.html'
    success_url = reverse_lazy('todos:todo_list')
    context_object_name = 'todo'
    
    def get_queryset(self):
        """Only allow users to delete their own todos."""
        return Todo.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Add page title to context."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Delete Task: {self.object.title}'
        return context
    
    def delete(self, request, *args, **kwargs):
        """
        Override delete method to ensure proper deletion and show success message.
        This is the FIX that makes deletion work.
        """
        try:
            # Get the todo object
            self.object = self.get_object()
            todo_title = self.object.title
            
            # Double-check ownership
            if self.object.user != request.user:
                messages.error(request, "You don't have permission to delete this task.")
                return redirect('todos:todo_list')
            
            # Perform the deletion
            self.object.delete()
            
            # Show success message
            messages.success(
                request,
                f'Task "{todo_title}" has been deleted successfully!'
            )
            
            return redirect(self.success_url)
            
        except Todo.DoesNotExist:
            messages.error(request, "Task not found or already deleted.")
            return redirect('todos:todo_list')
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error deleting todo: {str(e)}")
            
            messages.error(request, "An error occurred while deleting the task.")
            return redirect('todos:todo_list')


@login_required
def toggle_completion(request, pk):
    """
    Toggle completion status of a todo (only if user owns it).
    """
    # Get todo that belongs to current user
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    
    # Toggle completion
    todo.completed = not todo.completed
    todo.save()
    
    # Show appropriate message
    status = "completed" if todo.completed else "marked as active"
    messages.info(request, f'Task "{todo.title}" {status}.')
    
    return redirect('todos:todo_list')


class RegisterView(View):
    """
    Handle user registration.
    """
    template_name = 'registration/register.html'
    form_class = RegisterForm
    
    def get(self, request):
        """Show registration form."""
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in!")
            return redirect('todos:todo_list')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        """Process registration form."""
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create profile for new user
            Profile.objects.get_or_create(user=user)
            
            # Log the user in
            login(request, user)
            
            messages.success(request, f"Welcome, {user.username}! Account created successfully!")
            return redirect('todos:todo_list')
        else:
            messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    """
    Handle user login.
    """
    template_name = 'registration/login.html'
    form_class = LoginForm
    
    def get(self, request):
        """Show login form."""
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in!")
            return redirect('todos:todo_list')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        """Process login form."""
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('todos:todo_list')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {'form': form})


@login_required
def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('todos:login')


@login_required
def profile(request):
    """
    Handle user profile updates.
    """
    # Get or create user profile
    profile_instance, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=profile_instance
        )
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('todos:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile_instance)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    
    return render(request, 'registration/profile.html', context)