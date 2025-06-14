"""
Template filters for displaying times in the user's timezone
"""
from django import template
from django.utils import timezone
from django.utils.dateformat import format as date_format
import pytz

from gym.constants import DATETIME_FORMAT, DATE_FORMAT, TIME_FORMAT

register = template.Library()

@register.filter
def in_user_timezone(value, tz_name):
    """
    Convert a datetime to the user's timezone
    
    Usage:
    {{ session.start_time|in_user_timezone:user_timezone }}
    
    Args:
        value: The datetime to convert
        tz_name: The name of the timezone to convert to
        
    Returns:
        The datetime in the user's timezone
    """
    if not value:
        return value
        
    # Make sure the value is timezone-aware
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.utc)
        
    # Convert to the user's timezone
    try:
        user_tz = pytz.timezone(tz_name)
        return value.astimezone(user_tz)
    except:
        # If there's an error, just return the original value
        return value
        
@register.filter
def format_datetime(value, format_string=None):
    """
    Format a datetime using the given format string
    
    Usage:
    {{ session.start_time|in_user_timezone:user_timezone|format_datetime }}
    
    Args:
        value: The datetime to format
        format_string: The format string to use, or None to use default DATETIME_FORMAT
        
    Returns:
        The formatted datetime
    """
    if not value:
        return ""
    
    if format_string is None:
        format_string = DATETIME_FORMAT
        
    try:
        return date_format(value, format_string)
    except Exception as e:
        # Print the error for debugging
        print(f"Error formatting datetime: {e}")
        return str(value)

@register.simple_tag
def format_datetime_in_timezone(value, tz_name, format_string=None):
    """
    Convert a datetime to the user's timezone and format it
    
    Usage:
    {% format_datetime_in_timezone session.start_time user_timezone %}
    
    Args:
        value: The datetime to convert and format
        tz_name: The name of the timezone to convert to
        format_string: The format string to use, or None to use default DATETIME_FORMAT
        
    Returns:
        The formatted datetime in the user's timezone
    """
    if not value:
        return ""
    
    if format_string is None:
        format_string = DATETIME_FORMAT
        
    try:
        # Make sure the value is timezone-aware
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.utc)
            
        # Convert to the user's timezone
        user_tz = pytz.timezone(tz_name)
        value = value.astimezone(user_tz)
        
        # Format the datetime
        return date_format(value, format_string)
    except Exception as e:
        # Print the error for debugging
        print(f"Error formatting datetime in timezone: {e}")
        return str(value)

@register.simple_tag
def format_date_in_timezone(value, tz_name):
    """
    Convert a datetime to the user's timezone and format it as a date only
    
    Usage:
    {% format_date_in_timezone session.start_time user_timezone %}
    
    Args:
        value: The datetime to convert and format
        tz_name: The name of the timezone to convert to
        
    Returns:
        The formatted date in the user's timezone
    """
    if not value:
        return ""
        
    try:
        # Make sure the value is timezone-aware
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.utc)
            
        # Convert to the user's timezone
        user_tz = pytz.timezone(tz_name)
        value = value.astimezone(user_tz)
        
        # Format the date
        return date_format(value, DATE_FORMAT)
    except Exception as e:
        # Print the error for debugging
        print(f"Error formatting date in timezone: {e}")
        return str(value)

@register.simple_tag
def format_time_in_timezone(value, tz_name):
    """
    Convert a datetime to the user's timezone and format it as a time only
    
    Usage:
    {% format_time_in_timezone session.start_time user_timezone %}
    
    Args:
        value: The datetime to convert and format
        tz_name: The name of the timezone to convert to
        
    Returns:
        The formatted time in the user's timezone
    """
    if not value:
        return ""
        
    try:
        # Make sure the value is timezone-aware
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.utc)
            
        # Convert to the user's timezone
        user_tz = pytz.timezone(tz_name)
        value = value.astimezone(user_tz)
        
        # Format the time
        return date_format(value, TIME_FORMAT)
    except Exception as e:
        # Print the error for debugging
        print(f"Error formatting time in timezone: {e}")
        return str(value)