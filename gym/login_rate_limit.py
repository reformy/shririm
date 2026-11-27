"""Limit failed logins per client IP, so passwords can't be guessed by trying many."""
from functools import wraps

from django.http import HttpResponse
from django_ratelimit.core import get_usage, is_ratelimited

GROUP = 'login.failed'
# Failed logins per client IP (see client_ip). Only failures count, so logging in works for people on the
# same IP as a guesser until it is blocked.
FAILED_RATE = '20/h'


def client_ip(request) -> str:
    """
    The client's IP address, for django-ratelimit (settings.RATELIMIT_IP_META_KEY).

    On PythonAnywhere REMOTE_ADDR is the load balancer's internal address; the balancer puts the real client
    address in X-Real-IP. Locally there is no balancer, so fall back to REMOTE_ADDR.
    """
    return request.META.get('HTTP_X_REAL_IP') or request.META['REMOTE_ADDR']


def rate_limited_login(view):
    """
    Wraps a login view (the gym's, or the admin's). A failed login is a POST that shows the form again (200);
    a successful one redirects.
    """
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.method != 'POST':
            return view(request, *args, **kwargs)
        usage = get_usage(request, group=GROUP, key='ip', rate=FAILED_RATE, increment=False)
        if usage and usage['count'] >= usage['limit']:
            # The count is reset at the end of a fixed window, not an hour after the last failure.
            minutes = max(1, -(-usage['time_left'] // 60))
            unit = 'minute' if minutes == 1 else 'minutes'
            return HttpResponse(f'Too many failed logins. Try again in {minutes} {unit}.', status=429,
                                content_type='text/plain')
        response = view(request, *args, **kwargs)
        if response.status_code == 200:
            is_ratelimited(request, group=GROUP, key='ip', rate=FAILED_RATE, increment=True)
        return response
    return wrapper
