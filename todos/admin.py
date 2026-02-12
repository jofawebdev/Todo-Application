from django.contrib import admin
from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Todo model.
    
    Features:
    - List display with completion status indicators
    - List filters for priority and completion
    - Search functionality
    - Read-only fields for timestamps
    """
    # Fields to display in list view
    list_display = [
        'title', 
        'priority_display', 
        'completed', 
        'due_date', 
        'days_until_due_display',
        'created_at'
    ]
    
    # Filter options in sidebar
    list_filter = ['completed', 'priority', 'due_date']
    
    # Search fields
    search_fields = ['title', 'description']
    
    # Fields that can be edited directly in list view
    list_editable = ['completed']
    
    # Fields to show in detail/edit view
    fieldsets = (
        ('Task Details', {
            'fields': ('title', 'description', 'priority', 'due_date')
        }),
        ('Status', {
            'fields': ('completed',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapsible section
        }),
    )
    
    # Read-only fields
    readonly_fields = ['created_at', 'updated_at']
    
    # Custom list display methods
    def priority_display(self, obj):
        """Display priority with stars."""
        return '⭐' * obj.priority
    priority_display.short_description = 'Priority'
    
    def days_until_due_display(self, obj):
        """Display days until due with color coding."""
        days = obj.days_until_due()
        if days is None:
            return 'No due date'
        elif days < 0:
            return f'Overdue ({abs(days)} days)'
        elif days == 0:
            return 'Due today'
        else:
            return f'{days} days'
    days_until_due_display.short_description = 'Due In'