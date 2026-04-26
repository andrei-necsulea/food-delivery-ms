from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def role_required(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.role not in allowed_roles:
                return HttpResponseForbidden("Access denied: insufficient permissions.")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator