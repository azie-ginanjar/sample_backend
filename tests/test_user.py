import json

import factory
from pytest_factoryboy import register

from rodenia_api.constants import DefaultUserSetting, EmailTypes
from rodenia_api.models import User, ResetToken


@register
class UserFactory(factory.Factory):
    username = factory.Sequence(lambda n: 'user%d' % n)
    email = factory.Sequence(lambda n: 'user%d@mail.com' % n)
    password = "mypwd"
    role = "user"

    class Meta:
        model = User


def test_generate_reset_token(client, db, admin_headers):
    # test generate reset token
    email = "admin@admin.com"
    user = User.query.filter_by(email=email).first()
    assert user is not None
    res = client.post("/auth/generate_reset_token", json={"email": email})
    assert res.status_code == 200
    assert ResetToken.query.filter_by(user_id=user.id).first() is not None


def test_generate_reset_token_on_bad_email(client, db):
    # test generate reset token
    res = client.post("/auth/generate_reset_token", json={"email": "dsfasfdf@gmail.com"})
    assert res.status_code == 200
    assert 'error' in str(res.data)


def test_reset_password(client, db, admin_headers):
    # test reset password
    email = "admin@admin.com"
    user = User.query.filter_by(email=email).first()
    assert user is not None

    res = client.post("/auth/generate_reset_token", json={"email": email})
    assert res.status_code == 200

    reset_token = ResetToken.query.filter_by(user_id=user.id).first()
    assert reset_token is not None

    # test passwords don't match will be rejected
    res = client.post("/auth/reset_password", json={
        "token_str": reset_token.token_str,
        "password": "abcdef",
        "password_2": "asdfasdfasdfasdf"
    })
    assert res.status_code == 200
    assert 'error' in str(res.data)

    # test fake token all will be rejected
    res = client.post("/auth/reset_password", json={
        "token_str": "blablablathisshouldn'texist",
        "password": "abcdef",
        "password_2": "abcdef"
    })
    assert res.status_code == 200
    assert 'error' in str(res.data)

    res = client.post("/auth/reset_password", json={
        "token_str": reset_token.token_str,
        "password": "abcdef",
        "password_2": "abcdef"
    })
    assert res.status_code == 200


def test_login_with_email(client, db, admin_headers):
    # test generate reset token
    res = client.post("/auth/login", json={"username_or_email": "admin@admin.com", "password": "admin"})
    assert res.status_code == 200


def test_login_with_username(client, db, admin_headers):
    # test generate reset token
    res = client.post("/auth/login", json={"username_or_email": "admin", "password": "admin"})
    assert res.status_code == 200


def test_login_is_case_insensitive(client, db, admin_headers):
    # test generate reset token
    res = client.post("/auth/login", json={"username_or_email": "ADmIn", "password": "admin"})
    assert res.status_code == 200


def test_login_fails(client, db, admin_headers):
    # test generate reset token
    res = client.post("/auth/login", json={"username_or_email": "admin@admin.com", "password": "abcdef"})
    assert res.status_code == 200
    assert 'error' in str(res.data)


def test_registration(client, db):
    # test registration
    res = client.post("/auth/registration", json={
        "username": "test_user",  # use plan_id to make each username unique
        "email": "test_user@gmail.com",
        "password": "abc1231"
    })

    res_json = json.loads(res.data)
    assert res.status_code == 200
    assert res_json['username'] == 'test_user'


def test_duplicate_registration_fails(client, db, admin_headers):
    # test generate reset token

    res = client.post("/auth/registration", json={
        "username": "jeff",
        "email": "jeff@gmail.com",
        "password": "abc",
        "registrationPlanId": "standard",
        "stripeToken": "faketoken"
    })
    assert res.status_code == 200

    res = client.post("/auth/registration", json={
        "username": "jeff",
        "email": "jeff@gmail.com",
        "password": "abc",
        "registrationPlanId": "standard",
        "stripeToken": "faketoken"
    })
    assert res.status_code == 400
    assert 'error' in str(res.data)


def test_duplicate_registration_fails_even_if_case_changes(client, db, admin_headers):
    # test generate reset token

    res = client.post("/auth/registration", json={
        "username": "JeFfDh5",
        "email": "jeff@gmail.com",
        "password": "abc",
        "registrationPlanId": "standard",
        "stripeToken": "faketoken"
    })
    assert res.status_code == 200

    res = client.post("/auth/registration", json={
        "username": "jeff",
        "email": "jeff@gmail.com",
        "password": "abc",
        "registrationPlanId": "standard",
        "stripeToken": "faketoken"
    })
    assert res.status_code == 400
    assert 'error' in str(res.data)


def test_update_email_setting(client, db, access_token_with_test_user_by_endpoint):
    res = client.put("/api/v1/user/setting",
                     json={
                         "email_from_name": "admin",
                         "email_reply_to": "admin@myweb.com",
                         "email_footer_address": "test"
                     },
                     headers={
                         'Authorization': 'Bearer ' + access_token_with_test_user_by_endpoint
                     })

    assert res.status_code == 200
    json_response = json.loads(res.data)
    assert json_response['user_setting']['email_from_name'] == 'admin'


def test_update_email_template(client, db, access_token_with_test_user_by_endpoint):
    res = client.put("/api/v1/user/setting/email_template",
                     json={
                         "email_type": "coupon_email",
                         "email_subject": "your email voucher",
                         "email_heandline": "xxxxx",
                         "email_body": "xxxxx"
                     },
                     headers={
                         'Authorization': 'Bearer ' + access_token_with_test_user_by_endpoint
                     })

    assert res.status_code == 200
    json_response = json.loads(res.data)
    assert json_response['email_template']['email_type'] == EmailTypes.COUPON_EMAIL


def test_get_email_template(client, db, access_token_with_test_user_by_endpoint):
    res = client.get("/api/v1/user/setting/email_template?email_type=coupon_email",
                     headers={
                         'Authorization': 'Bearer ' + access_token_with_test_user_by_endpoint
                     })

    assert res.status_code == 200


def test_update_active_country(client, db, access_token_with_test_user_by_endpoint):
    res = client.put("/api/v1/user/active_country",
                     json={
                         "country": "ph",
                     },
                     headers={
                         'Authorization': 'Bearer ' + access_token_with_test_user_by_endpoint
                     })

    assert res.status_code == 200
    q = User.query.filter(User.username == "test").first()
    assert q.active_country == "ph"


def test_update_active_country_invalid_req_body(client, db, access_token_with_test_user_by_endpoint):
    res = client.put("/api/v1/user/active_country",
                     json={
                         "invalid_name": "ph",
                     },
                     headers={
                         'Authorization': 'Bearer ' + access_token_with_test_user_by_endpoint
                     })

    assert res.status_code == 400
