from django import template
import math

register = template.Library()

@register.filter
def percentage_of(value, max_value):
    """
    Calculates what percentage of max_value is value
    
    Usage: {{ value|percentage_of:max_value }}
    """
    try:
        value = float(value)
        max_value = float(max_value)
        if max_value == 0:
            return 0
        return (value / max_value) * 100
    except (ValueError, TypeError):
        return 0
        
@register.filter
def multiply(value, arg):
    """
    Multiplies the value by the argument
    
    Usage: {{ value|multiply:factor }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value