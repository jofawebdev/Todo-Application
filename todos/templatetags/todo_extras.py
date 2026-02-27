"""
Custom template tags for the Todo app.
Provides a helper to modify query strings while preserving existing parameters.
"""
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """
    Generate a query string with updated parameters.

    This tag takes the current request's GET parameters and updates them
    with any keyword arguments passed. It returns a URL-encoded string
    suitable for appending to a URL.

    Usage in template:
        <a href="?{% query_transform page=2 %}">Next</a>

    This will keep all existing GET parameters (like 'q', 'status', 'priority')
    and change the 'page' parameter to 2. If the parameter already exists,
    it is overwritten; if the value is None, the parameter is removed.

    Args:
        context: The template context (automatically provided by Django).
        **kwargs: Key-value pairs to update in the query string.

    Returns:
        str: URL-encoded query string (without the leading '?').
    """
    # Get the current request object from the context
    request = context['request']
    # Make a mutable copy of the current GET parameters
    query_dict = request.GET.copy()

    # Update the dictionary with any new parameters
    for key, value in kwargs.items():
        if value is not None:
            query_dict[key] = str(value)
        else:
            # Remove the key if the value is None (e.g., to clear a filter)
            query_dict.pop(key, None)

    # Return the URL-encoded string
    return query_dict.urlencode()