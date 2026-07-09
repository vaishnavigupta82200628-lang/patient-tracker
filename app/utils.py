from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*roles):
    """
    Custom decorator to restrict access based on user role.
    Usage: @role_required('admin')  or  @role_required('admin', 'doctor')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)  # Forbidden
            if current_user.role not in roles:
                abort(403)  # Forbidden - wrong role
            return f(*args, **kwargs)
        return decorated_function
    return decorator