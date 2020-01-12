from rodenia_api.models import User


def validate_user_registration_payload(request_data):
    username = request_data.get('username')
    email = request_data.get('email')
    password = request_data.get('password')

    if not username or not password:
        return {
            'is_valid': False,
            'message': 'Missing username or password'
        }

    if not email:
        return {
            'is_valid': False,
            'message': 'Missing email'
        }

    user_by_username = User.query.filter_by(username=username.lower()).first()

    if user_by_username:
        return {
            'is_valid': False,
            'message': 'Username already exists'
        }

    user_by_email = User.query.filter_by(email=email.lower()).first()
    if user_by_email is not None:
        return {
            'is_valid': False,
            'message': 'Email already exists'
        }

    return {
        'is_valid': True,
        'username': username,
        'password': password,
        'email': email
    }
