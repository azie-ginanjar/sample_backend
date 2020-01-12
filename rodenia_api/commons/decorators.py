from functools import wraps
from flask_jwt_extended import jwt_required, get_current_user
from rodenia_api.commons.exceptions import PermissionDeniedException
from flask import request


def admin_required(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        current_user = get_current_user()

        if current_user.role == 'admin':
            authorized = True
        else:
            authorized = False

        if not authorized:
            raise PermissionDeniedException("Insufficient Privilege")

        return view_function(*args, **kwargs)

    return jwt_required(wrapper)


def api_key_required(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):

        api_key = request.args.get("api_key")

        if not api_key:
            raise PermissionDeniedException("Permission denied for resource - No API Key Provided")

        authorized = api_key == "6qOotVfM51"        
        if not authorized:
            raise PermissionDeniedException("Permission denied for resource - Invalid API key")

        return view_function(*args, **kwargs)
    return wrapper
