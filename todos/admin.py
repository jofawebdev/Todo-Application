from django.contrib import admin
from .models import Todo, Category, Profile


# ---------- Category Admin ----------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model.
    """
    list_display = ['name', 'user', 'color', 'todo_count']
    list_filter = ['user']
    search_fields = ['name']
    list_editable = ['color']  # Quick color editing from list view
    fieldsets = (
        (None, {
            'fields': ('name', 'user', 'color')
        }),
    )

    def todo_count(self, obj):
        """Display number of todos in this category."""
        return obj.todos.count()
    todo_count.short_description = 'Tasks'


# ---------- Todo Admin ----------
@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Todo model.
    
    Features:
    - List display with completion status indicators
    - List filters for priority, completion, and categories
    - Search functionality
    - Read-only fields for timestamps
    - Many-to-many field for categories with filter horizontal widget
    """
    # Fields to display in list view
    list_display = [
        'title', 
        'priority_display', 
        'completed', 
        'due_date', 
        'days_until_due_display',
        'created_at',
        'category_list'  # Added: show categories as a short list
    ]
    
    # Filter options in sidebar
    list_filter = [
        'completed', 
        'priority', 
        'due_date',
        'categories'  # Added: filter by category
    ]
    
    # Search fields
    search_fields = ['title', 'description']
    
    # Fields that can be edited directly in list view
    list_editable = ['completed']
    
    # Improve performance for many-to-many fields
    filter_horizontal = ['categories']  # Adds a nice horizontal filter widget
    
    # Fields to show in detail/edit view
    fieldsets = (
        ('Task Details', {
            'fields': ('title', 'description', 'priority', 'due_date')
        }),
        ('Categorization', {
            'fields': ('categories',),
            'classes': ('wide',),
            'description': 'Assign this task to one or more categories.'
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
    
    def category_list(self, obj):
        """Return a comma-separated list of category names."""
        return ", ".join([cat.name for cat in obj.categories.all()])
    category_list.short_description = 'Categories'


# Optionally register Profile if you want it in admin
# (You may already have it, but it's not included in the original file)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'image']
    search_fields = ['user__username']