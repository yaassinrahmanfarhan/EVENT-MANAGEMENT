from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def role_required(*roles):
    """Restrict access to users in specific Django Groups."""
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name__in=roles).exists():
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You do not have permission to access this page.")
        return _wrapped_view
    return decorator