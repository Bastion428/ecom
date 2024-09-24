from django.shortcuts import redirect
from django.contrib import messages
import functools


def required_methods_redirect(func, allowed_methods=['GET']):
    """Redirects when method is not POST"""
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        method_list = [allowed_methods] if isinstance(allowed_methods, str) else allowed_methods
        if request.method in method_list:
            return func(request, *args, **kwargs)
        else:
            messages.error(request, f'{request.method} is not an accepted method for the requested page. Access denied')
            return redirect('home')
    return wrapper
