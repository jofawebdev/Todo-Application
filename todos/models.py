"""
Models for the Todo application.
Defines Todo items with user ownership and related functionality.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image


class Todo(models.Model):
    """
    Todo model representing a task with various attributes.
    
    Fields:
    - user: The owner of the todo (ForeignKey to User) - ADDED
    - title: Short descriptive title (required)
    - description: Detailed explanation of the task (optional)
    - completed: Boolean flag indicating completion status
    - priority: Integer 1-5 (1=lowest, 5=highest) with visual representation
    - due_date: Optional deadline for the task
    - created_at: Auto-set timestamp when task is created
    - updated_at: Auto-updated timestamp on modification
    """
    
    # Priority choices for better readability in forms and admin
    PRIORITY_CHOICES = [
        (1, '⭐ Very Low'),
        (2, '⭐⭐ Low'),
        (3, '⭐⭐⭐ Medium'),
        (4, '⭐⭐⭐⭐ High'),
        (5, '⭐⭐⭐⭐⭐ Critical'),
    ]
    
    # User ownership - each todo belongs to a specific user - ADDED
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='todos',
        verbose_name="Owner",
        help_text="User who owns this task",
        null=True,  # Temporarily nullable for migration
        blank=True  # Temporarily blank for migration
    )
    
    # Required field: Short, descriptive title
    title = models.CharField(
        max_length=200,
        verbose_name="Task Title",
        help_text="Enter a brief, descriptive title for your task"
    )
    
    # Optional detailed description
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Add more details about your task (optional)"
    )
    
    # Completion status with default of False
    completed = models.BooleanField(
        default=False,
        verbose_name="Completed",
        help_text="Mark as completed when task is done"
    )
    
    # Priority with validation and default value
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Priority Level",
        help_text="Select priority from 1 (lowest) to 5 (highest)"
    )
    
    # Optional due date with date picker in forms
    due_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Due Date",
        help_text="Set a deadline for this task (optional)"
    )
    
    # Auto-managed timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    
    class Meta:
        """
        Meta Options for the Todo Model.
        """
        ordering = ['-priority', 'completed', 'due_date']  # Sort by priority, then completion, then due date
        verbose_name = "Todo Item"
        verbose_name_plural = "Todo Items"
        
    def __str__(self):
        """
        String representation of Todo item.
        """
        status = "✓" if self.completed else "○"
        owner = self.user.username if self.user else "No Owner"
        return f"{status} {self.title} ({owner})"
    
    def get_absolute_url(self):
        """Get URL for this todo (used by Django admin and generic views)."""
        return reverse('todos:todo_update', kwargs={'pk': self.pk})
    
    def is_overdue(self):
        """
        Check if the todo is past its due date and not completed.
        """
        if self.due_date and not self.completed:
            return self.due_date < timezone.now().date()
        return False
    
    def days_until_due(self):
        """
        Calculate days until due date (negative if overdue)
        """
        if self.due_date:
            delta = self.due_date - timezone.now().date()
            return delta.days
        return None
    
    def save(self, *args, **kwargs):
        """Override save to ensure user is set for new todos."""
        # This check prevents saving todos without a user (except in admin maybe)
        if not self.pk and not self.user:
            raise ValueError("Todo must have a user")
        super().save(*args, **kwargs)


class Profile(models.Model):
    """
    User profile model with profile picture.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        default='default.jpg',
        upload_to='profile_pics',
        help_text="Upload a profile picture (300x300 recommended)"
    )
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        """
        Override save method to resize profile images.
        """
        super().save(*args, **kwargs)
        
        # Resize image if it's too large
        img = Image.open(self.image.path)
        
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)