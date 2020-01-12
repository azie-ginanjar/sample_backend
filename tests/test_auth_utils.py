from rodenia_api.libraries.auth_lib.auth_utils import validate_user_registration_payload


def test_validate_user_registration_payload(db, test_user):
    valid_payload = {
        'username': 'user1',
        'password': 'password1',
        'email': 'myemail@mail.com'
    }

    payloadwith_existing_email = {
        'username': 'user1',
        'password': 'password1',
        'email': test_user.email
    }

    payloadwith_existing_username = {
        'username': test_user.username,
        'password': 'password1',
        'email': 'myemail@mail.com'
    }

    payload_with_missing_email = {
        'username': 'user1',
        'password': 'password1'
    }

    payload_with_missing_username = {
        'password': 'password1',
        'email': 'myemail@mail.com'
    }

    payload_with_missing_password = {
        'username': 'user1',
        'email': 'myemail@mail.com'
    }

    validate_with_missing_email = validate_user_registration_payload(payload_with_missing_email)
    assert not validate_with_missing_email['is_valid']
    assert validate_with_missing_email['message'] == 'Missing email'

    validate_with_missing_username = validate_user_registration_payload(payload_with_missing_username)
    assert not validate_with_missing_username['is_valid']
    assert validate_with_missing_username['message'] == 'Missing username or password'

    validate_with_missing_password = validate_user_registration_payload(payload_with_missing_password)
    assert not validate_with_missing_password['is_valid']
    assert validate_with_missing_password['message'] == 'Missing username or password'

    validate_with_valid_payload = validate_user_registration_payload(valid_payload)
    assert validate_with_valid_payload['is_valid']

    validate_with_existing_email = validate_user_registration_payload(payloadwith_existing_email)
    assert not validate_with_existing_email['is_valid']
    assert validate_with_existing_email['message'] == 'Email already exists'

    validate_with_existing_username = validate_user_registration_payload(payloadwith_existing_username)
    assert not validate_with_existing_username['is_valid']
    assert validate_with_existing_username['message'] == 'Username already exists'
