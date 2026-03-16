from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Todo, Profile, Category # Added category


class CategoryForm(forms.ModelForm):
    """
    Form for creating and editing categories
    The user is not a field on the form; it is set in the view.
    """
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Work',
                'autofocus': True
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',           # HTML5 color picker
                'class': 'form-control form-control-color',
                'style': 'width: 100px;'
            }),
        }
        labels = {
            'name': 'Category Name',
            'color': 'Badge Color',
        }
        
    def clean_name(self):
        name = self.cleaned_data.get('name').strip()
        if len(name) < 2:
            raise ValidationError("Category name must be at least 2 characters.")
        return name


class TodoForm(forms.ModelForm):
    """
    ModelForm fo creating and updating Todo Items
    Features:
    - Custom widgets for better UX
    - Clean validation for due dates
    - Priority display with stars
    - Now includes a categories field limited to the current user's categories
    """
    
    class Meta:
        model = Todo
        fields = ['title', 'description', 'priority', 'due_date', 'categories']
        
        # Custom widgets for better user experience
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'What needs to be done?',
                'autofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Add details, notes, or context...',
                'rows': 4,
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-date',
                'min': timezone.now().date().isoformat(), # Prevent past dates
            }),
            # Use checkboxes for categories - we'll set the queryset in __init__
            'categories': forms.CheckboxSelectMultiple(),
        }
        
        # Custom labels and help texts
        labels = {
            'title': 'Task Title',
            'description': 'Details',
            'priority': 'Priority Level',
            'due_date': 'Due Date',
            'categories': 'Assign Categories',
        }
        
    def __init__(self, *args, **kwargs):
        """
        Pop the 'user' keyword argument and use it to limit the categories queryset.
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Only show categories that belong to this user
            self.fields['categories'].queryset = Category.objects.filter(user=user)
        else:
            # Fallback: empty queryset (should not happen when used in views)
            self.fields['categories'].queryset = Category.objects.none()
            
        # Make categories optional
        self.fields['categories'].required = False
        
        
    def clean_due_date(self):
        """
        Validate due_date to ensure it's not in the past.
        
        Returns:
            The cleaned due_date if valid
            
        Raise:
            ValidationError if due_date is in the past
        """
        due_date = self.cleaned_data.get('due_date')
        
        if due_date:
            if due_date < timezone.now().date():
                raise ValidationError("Due date cannot be in the past.")
            
        return due_date
    
    
    def clean_title(self):
        """
        Validate title to ensure it's meaningful.
        
        Returns:
            Stripped title if valid
            
        Raises:
            ValidationError if title is too short
        """
        title = self.cleaned_data.get('title', '').strip()
        
        if len(title) < 3:
            raise ValidationError("Title must be atleast 3 characters long.")
        
        return title
    
    
class RegisterForm(UserCreationForm):
    """
    Custom registration form extending Django's UserCreationForm.
    Adds email field with validation and Bootstrap styling.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email'}
        )
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Username'}
            )
        }
        
    def __init__(self, *args, **kwargs):
        """
        Initialize form with Bootstrap classes for password fields.
        """
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
        
    def clean_email(self):
        """
        Validate that email is unique across all users.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email
    
class LoginForm(AuthenticationForm):
    """
    Custom Login form with Bootstrap styling.
    """
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Username'}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'}
        )
    )
    
class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile picture
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize form with Bootstrap classes for the image field.
        """
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to the image field
        self.fields['image'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })
        
    class Meta:
        model = Profile
        fields = ['image']
        
    def clean_image(self):
        """
        Validate profile image size and format.
        """
        image = self.cleaned_data.get('image')
        
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large (>5MB)")
            
            # Check file extension
            valid_extensions = ['jpg', 'jpeg', 'png','gif', 'webp']
            extension = image.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise ValidationError(
                    f"Unsupported file extension. Allowed: {', '.join(valid_extensions)}"
                )
                
        return image
    
    
# Update the UserUpdateForm class
class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user information (username and email).
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
        
    def clean_email(self):
        """
        Validate that email is unique across all users (excluding current user).
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email address is already in use.")
        return email