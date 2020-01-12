import io
import json
import pytest

from rodenia_api.models import User
from rodenia_api.app import create_app
from rodenia_api.extensions import db as _db


@pytest.fixture
def app():
    app = create_app(testing=True)
    return app


@pytest.fixture
def db(app):
    _db.app = app

    with app.app_context():
        _db.create_all()

    yield _db

    _db.session.close()
    _db.drop_all()


@pytest.fixture
def client(app):
    flask_app = app
    testing_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()


@pytest.fixture
def admin_user(db):
    user = User(
        username='admin',
        email='admin@admin.com',
        password='admin',
        role='admin'
    )

    db.session.add(user)
    db.session.commit()

    return user


@pytest.fixture
def admin_headers(admin_user, client):
    data = {
        'username_or_email': admin_user.username,
        'password': 'admin'
    }
    rep = client.post(
        '/auth/login',
        data=json.dumps(data),
        headers={'content-type': 'application/json'}
    )

    # print(rep.get_data(as_text=True))
    tokens = json.loads(rep.get_data(as_text=True))
    return {
        'content-type': 'application/json',
        'authorization': 'Bearer %s' % tokens['access_token']
    }


@pytest.fixture
def test_user(db):
    user = User(
        username='test',
        email='test@test.com',
        password='test',
        role='user',
        marketplace_id='test_marketplace_id',
        has_active_subscription=True
    )

    db.session.add(user)
    db.session.commit()

    return user


@pytest.fixture
def test_user_by_endpoint(client):
    res = client.post("/auth/registration", json={
        "username": "test",  # use plan_id to make each username unique
        "email": "test@test.com",
        "password": "test"
    })

    res_json = json.loads(res.data)
    # print(res_json)
    return res_json['user']


@pytest.fixture
def another_test_user(db):
    user = User(
        user_id="123",
        username='test1',
        email='test1@test.com',
        password='test1',
        role='user'
    )

    db.session.add(user)
    db.session.commit()

    return user


@pytest.fixture
def access_token(client, test_user):
    res = client.post("/auth/login", json={
        "username_or_email": test_user.username,
        "password": "test"
    })
    json_data = json.loads(res.data)
    # print(json_data)
    return json_data['access_token']


@pytest.fixture
def access_token_with_test_user_by_endpoint(client, test_user_by_endpoint):
    res = client.post("/auth/login", json={
        "username_or_email": test_user_by_endpoint['username'],
        "password": test_user_by_endpoint['password']
    })
    json_data = json.loads(res.data)
    # print(json_data)
    return json_data['access_token']


@pytest.fixture
def access_token_with_test_user_by_endpoint(client, test_user_by_endpoint):
    res = client.post("/auth/login", json={
        "username_or_email": test_user_by_endpoint['username'],
        "password": "test"
    })
    json_data = json.loads(res.data)
    # print(json_data)
    return json_data['access_token']


@pytest.fixture
def access_token_another(client, another_test_user):
    res = client.post("/auth/login", json={
        "username_or_email": another_test_user.email,
        "password": "test1"
    })
    json_data = json.loads(res.data)
    # print(json_data)
    return json_data['access_token']


@pytest.fixture
def set_env_for_shopee(monkeypatch):
    monkeypatch.setenv('SHOPEE_PARTNER_ID', '123123')
    monkeypatch.setenv('SHOPEE_SECRET_KEY', 'fake difficult string')