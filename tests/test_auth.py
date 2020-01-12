from rodenia_api.models import User
from rodenia_api.clock_helpers.constants import SHOPEE_ORDER_STATUS_ENUM
from unittest.mock import Mock, patch
import json


@patch('rodenia_api.auth.namespaces.auth.system.generate_access_token')
def test_lazada_auth_callback_successful(lazada_api, client, access_token, test_user):
    """
    case where lazada call was successful and returned access token
    and there was no error updating user record
    """
    lazada_api.return_value = Mock(body={u'account': u'ella.sherilyn.ramos@gmail.com', 
                                         u'code': u'0', u'access_token': u'50000800b29fOwiBo0RvahylWcLPbtQC6fAP3PR2j19472a42JmRjyluZknrA0',
                                         u'country': u'ph', u'expires_in': 604800, u'request_id': u'0b8fda7b15501212252766562',
                                         u'refresh_expires_in': 2592000, u'account_platform': u'seller_center',
                                         u'country_user_info': [{u'short_code': u'PHJ2F8MX', u'country': u'ph',
                                                                u'seller_id': u'1000069977', u'user_id': u'100255018'}], 
                                         u'refresh_token': u'50001800e29jhdwoqeD4g2cnSZVOeYDAP7KRtHFmQ145db664K4ltvHgdjzjcV'}, message=None)

    res = client.post("/auth/lazada_auth_callback",
        headers={
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        },
        json={
            "code": "0_108647_7LaCotddGRvLahUEPXdev1R92743"
        }
    )
    user = User.find_user_by_username(test_user.username)
    marketplace = LazadaMarketplace.query.filter_by(user=user, seller_id='1000069977').first()

    assert marketplace.country == 'ph'
    assert marketplace.access_token == '50000800b29fOwiBo0RvahylWcLPbtQC6fAP3PR2j19472a42JmRjyluZknrA0'
    assert marketplace.refresh_token == '50001800e29jhdwoqeD4g2cnSZVOeYDAP7KRtHFmQ145db664K4ltvHgdjzjcV'
    assert marketplace.access_token_expiration == 604800
    assert marketplace.refresh_token_expiration == 2592000
    assert json.loads(res.data).get("user_id") == user.id
    assert json.loads(res.data).get("seller_id") == '1000069977'
    assert res.status_code == 200
    assert user.active_country.lower() == 'ph'


def test_lazada_auth_callback_missing_code(client, access_token, test_user):
    """
    case where code is missing from the payload
    """
    res = client.post("/auth/lazada_auth_callback",
        headers={
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        },
        json={
        }
    )

    assert res.status_code == 400


@patch('rodenia_api.auth.namespaces.auth.system.generate_access_token')
def test_lazada_auth_callback_unsuccessful(lazada_api, client, access_token, test_user):
    """
    case where lazada api call was successful but returned an error
    """
    lazada_api.return_value = Mock(body={u'message': u'Missing parameter', u'code': u'MissingParameter', 
                                         u'type': u'ISP', u'request_id': u'0baa047515502325142418546'}, message='Missing parameter')

    res = client.post("/auth/lazada_auth_callback",
        headers={
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        },
        json={
            "code": "0_108647_7LaCotddGRvLahUEPXdev1R92743"
        }
    )

    res_json = json.loads(res.data)
    assert "error" in res_json
    assert res_json.get("error") == "Missing parameter"
    assert res.status_code == 200


@patch('rodenia_api.auth.namespaces.auth.system.generate_access_token')
def test_lazada_auth_callback_raised_error(lazada_api, client, access_token, test_user):
    """
    case where calling lazada api call failed and raised an exception
    """
    lazada_api.side_effect = Mock(side_effect=Exception('Raise Exception'))

    res = client.post("/auth/lazada_auth_callback",
        headers={
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        },
        json={
            "code": "0_108647_7LaCotddGRvLahUEPXdev1R92743"
        }
    )

    res_json = json.loads(res.data)
    assert "error" in res_json
    assert res.status_code == 200


@patch('rodenia_api.auth.namespaces.auth.q.enqueue_call')
@patch('rodenia_api.auth.namespaces.auth.shop.get_shop_info')
def test_shopee_auth_call_back_successful(shopee_api, enqueue_call, client, access_token, test_user, set_env_for_shopee):
    """
    case where shopee call was successful and it returned shop's info in dict
    """

    shopee_api.return_value = {
        "status": "NORMAL",
        "item_limit": 10000,
        "disable_make_offer": 0,
        "videos": [],
        "country": "PH",
        "shop_description": "",
        "shop_id": 124761188,
        "request_id": "Hz9q28LazQgEqDQclw4MK",
        "images": [],
        "shop_name": "essramos",
        "enable_display_unitno": False
    }

    res = client.post("/auth/shopee_auth_callback",
        headers={
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        },
        json={
            "shop_id": 124761188
        }
    )

    assert enqueue_call.call_count == len(SHOPEE_ORDER_STATUS_ENUM)
    user = User.find_user_by_username(test_user.username)
    marketplace = ShopeeMarketplace.query.filter_by(user=user, shop_id=124761188).first()
    # print(res.data)
    # print(db.engine.table_names())
    # print(marketplace, user)
    assert marketplace.country == 'PH'
    assert user.active_country == 'PH'
    assert marketplace.shop_id == 124761188
    assert json.loads(res.data).get("shop_id") == 124761188
    assert json.loads(res.data).get("user_id") == user.id
    assert res.status_code == 200


@patch('rodenia_api.auth.namespaces.auth.shop.get_shop_info')
def test_shopee_auth_call_back_failure(shopee_api, client, access_token, test_user, set_env_for_shopee):
    """
    case where shopee call returned an error like wrong signature, missing parameters
    """

    shopee_api.return_value = {
        'msg': 'Authentication signature calculation is wrong', 
        'request_id': '7b1rfhxN35gTCjHQ0RKlDY', 
        'error': 'error_auth'
    }

    res = client.post("/auth/shopee_auth_callback",
        headers={
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        },
        json={
            "shop_id": 124761188
        }
    )
    user = User.find_user_by_username(test_user.username)
    marketplace = ShopeeMarketplace.query.filter_by(user=user, shop_id=124761188).first()

    assert marketplace is None
    res_json = json.loads(res.data)
    assert res_json.get("error") is not None
    assert res.status_code == 200


def test_shopee_auth_call_back_missing_parameter(client, access_token, test_user, set_env_for_shopee):
    """
    case where shop_id is missing
    """

    res = client.post("/auth/shopee_auth_callback",
        headers={
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        },
        json={
            "invalid_param": 124761188
        }
    )

    assert res.status_code == 400


@patch('rodenia_api.auth.namespaces.auth.shop.get_shop_info')
def test_shopee_auth_callback_raised_error(shopee_api, client, access_token, test_user, set_env_for_shopee):
    """
    case where calling lazada api call failed and raised an exception
    """
    shopee_api.side_effect = Mock(side_effect=Exception('Raise Exception'))

    res = client.post("/auth/shopee_auth_callback",
        headers={
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        },
        json={
            "shop_id": 123456
        }
    )

    res_json = json.loads(res.data)
    assert res_json.get("error") is not None
    assert res.status_code == 200
