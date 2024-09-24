from django.shortcuts import redirect
from django.contrib import messages
import functools


def require_POST_redirect(func):
    """Redirects when method is not POST"""
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            return func(request, *args, **kwargs)
        else:
            messages.error(request, f'{request.method} in not an accepted method. Access denied')
            return redirect('home')
    return wrapper
