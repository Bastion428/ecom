from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def required_methods_redirect(allowed_methods):
    def decorator(func):
        """Redirects when method(s) not in the allowed methods. If more than one method, allowed methods must be list"""
        wraps(func)
        def wrapper(request, *args, **kwargs):  # noqa: E306
            method_list = [allowed_methods] if isinstance(allowed_methods, str) else allowed_methods
            if request.method in method_list:
                return func(request, *args, **kwargs)
            else:
                messages.error(request, f'{request.method} is not an accepted method for the requested page. Access denied')
                return redirect('home')
        return wrapper
    return decorator
