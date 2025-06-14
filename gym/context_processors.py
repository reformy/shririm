"""
Context processors for the gym app
"""
import pytz
from django.utils import timezone

def user_timezone(request):
    """
    Add the user's timezone to the template context
    """
    user_timezone = 'UTC'
    
    if request.user.is_authenticated:
        try:
            user_timezone = request.user.profile.timezone
        except:
            # If there's an error, default to UTC
            user_timezone = 'UTC'
    
    return {
        'user_timezone': user_timezone,
        'all_timezones': pytz.common_timezones,
    }