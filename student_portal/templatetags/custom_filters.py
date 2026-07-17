from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a string key"""
    if dictionary is None:
        return 'Not answered'
    return dictionary.get(str(key), 'Not answered')