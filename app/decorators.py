# app/decorators.py

from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user

def roles_required(*roles):
    """
    Decorator to restrict access to users with specific roles.
    Usage:
        @roles_required('admin')
        def admin_dashboard():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('routes.login', next=request.url))
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('routes.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
