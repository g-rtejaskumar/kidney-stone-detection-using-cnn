from django.shortcuts import redirect
from functools import wraps

def user_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'userid' not in request.session:
            return redirect('UserLogin')
        return view_func(request, *args, **kwargs)
    return wrapper