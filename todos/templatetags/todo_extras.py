"""
Custom template tags for the Todo app.
Provides helpers to modify query strings and compute accessible text colors.
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

    This will keep all existing GET parameters (like 'q', 'status', 'priority', 'category')
    and change the 'page' parameter to 2. If the parameter already exists,
    it is overwritten; if the value is None, the parameter is removed.
    Passing an empty string as value will set the parameter to an empty string,
    which may be interpreted as "no filter" by the view.

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


@register.filter
def text_color(hex_color):
    """
    Determine accessible text color (black or white) for a given background hex color.

    Given a hex color code (e.g., '#ffaa33' or 'ffaa33'), this filter returns
    '#000000' for light backgrounds or '#ffffff' for dark backgrounds,
    ensuring sufficient contrast for readability.

    Usage in template:
        <span style="color: {{ cat.color|text_color }};">{{ cat.name }}</span>

    Args:
        hex_color (str): A hex color code, with or without leading '#'.
                         Can be 3 or 6 characters long (e.g., 'faf' or 'ffaa33').

    Returns:
        str: '#000000' for light backgrounds, '#ffffff' for dark backgrounds.
             Returns '#000000' as a safe default if the input is invalid.
    """
    if not hex_color:
        return '#000000'  # default

    # Remove '#' if present
    hex_color = hex_color.lstrip('#')

    # Convert to RGB
    try:
        if len(hex_color) == 3:
            # Expand shorthand like 'faf' to 'ffaaff'
            r = int(hex_color[0] * 2, 16)
            g = int(hex_color[1] * 2, 16)
            b = int(hex_color[2] * 2, 16)
        elif len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        else:
            return '#000000'  # invalid length
    except ValueError:
        return '#000000'  # non-hex characters

    # Calculate relative luminance per ITU-R BT.709
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255

    # Return black for light backgrounds, white for dark
    return '#000000' if luminance > 0.5 else '#ffffff'