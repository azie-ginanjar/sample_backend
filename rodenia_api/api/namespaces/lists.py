import json

from flask import request
from flask_jwt_extended import jwt_required
from flask_restplus import Namespace, Resource, fields

from rodenia_api.commons.util import subscribe_list_member

api = Namespace('lists', description='Lists related operations')


@api.route("/<string:list_id>")
class ListMemberResource(Resource):
    method_decorators = []

    @api.expect(api.model('SubscribeListMemberFields', {
        'email': fields.String(required=True, description='email')
    }), validate=True)
    @api.response(201, 'Subscribe list member successfully.', api.model('SubscribeListMemberResponseModel', {
        'status': fields.String(description='status')
    }))
    def post(self, list_id):
        list_data = request.json

        email = list_data['email']

        try:
            subscribe_list_member(list_id, email)

            return {
                'status': 'success'
            }
        except Exception as e:
            json_error = json.loads(str(e).replace('\'', '"'))
            return {
                'status': 'failed',
                'message': json_error['detail']
            }
