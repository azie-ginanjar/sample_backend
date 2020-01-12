from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restplus import Namespace, Resource, fields

from rodenia_api.commons.decorators import admin_required
from rodenia_api.commons.email_utils_v2 import send_plain_email
from rodenia_api.commons.pagination import paginate
from rodenia_api.commons.schemas import UserSchema
from rodenia_api.constants import ArtistApprovalEmail, EmailTypes
from rodenia_api.extensions import db, sentry
from rodenia_api.models import User, EmailLog

api = Namespace('user', description='User related operations')

parser = api.parser()
parser.add_argument('Authorization', type=str, location='headers')

artist_response_fields = api.model('ArtistResponse', {
    'id': fields.Integer(),
    'email': fields.String(),
    'full_name': fields.String(),
    'professional_talent': fields.String(),
    'city': fields.String(),
    'state': fields.String(),
    'zipcode': fields.String(),
    'self_description': fields.String(),
    'facebook': fields.String(),
    'instagram': fields.String(),
    'twitter': fields.String(),
    'youtube': fields.String(),
    'pinterest': fields.String(),
    'role': fields.String(),
    'status': fields.String(),
    'image': fields.String()
})

artist_data_response_fields = api.model('ArtistDataResponse', {
    'total': fields.Integer(),
    'pages': fields.Integer(),
    "next": fields.String(),
    "prev": fields.String(),
    "results": fields.List(fields.Nested(artist_response_fields))
})


@api.route("/")
@api.doc(parser=parser)
class UserResource(Resource):
    method_decorators = [admin_required]

    query_parser = api.parser()
    query_parser.add_argument('role', required=False, location='args', type=str)
    query_parser.add_argument('status', required=False, location='args', type=str)
    query_parser.add_argument('page', required=False, type=int, help='by default equal to 1')
    query_parser.add_argument('page_size', required=False, type=int, help='by default equal to 10')

    @api.expect(query_parser, validate=True)
    @api.response(200, 'Get Users list successfully.', api.model('UsersReponseModel', {
        'status': fields.String(description='status'),
        'data': fields.Nested(artist_data_response_fields, description='users data')
    }))
    def get(self):
        role = request.args.get('role', None)
        status = request.args.get('status', None)

        users = User.query

        if role:
            users = users.filter(
                User.role == role
            )

        if status:
            users = users.filter(
                User.status == status
            )

        schema = UserSchema(many=True)
        data = paginate(users, schema)

        results = data['results']

        users = []
        for result in results:
            result.pop("password", None)
            result.pop("email_logs", None)

            users.append(result)

        data['results'] = users
        return {
            'status': 'success',
            'data': data
        }


@api.route("/artist/approval")
@api.doc(parser=parser)
class ArtistApprovalResource(Resource):
    method_decorators = [admin_required]

    @api.expect(api.model('ArtistApprovalFields', {
        'is_approve': fields.Boolean(required=True, description='True if approved'),
        'user_id': fields.Integer(required=True, description='Artist user id')
    }))
    @api.response(200, 'Approval succeed', api.model('ArtistApprovalResponse', {
        'status': fields.String(description='status'),
        'user': fields.Nested(artist_response_fields, description='user data')
    }))
    def put(self):
        approval_data = request.json

        is_approve = approval_data['is_approve']
        user_id = approval_data['user_id']

        user = User.get(user_id)

        try:
            if is_approve:
                setattr(user, 'status', 'approved')
                email_body = ArtistApprovalEmail.APPROVED_EMAIL_BODY
                plain_email_body = ArtistApprovalEmail.PLAIN_APPROVED_EMAIL_BODY
                send_email = send_plain_email(user.email, ArtistApprovalEmail.EMAIL_SUBJECT, plain_email_body, False,
                                              is_html=True, html_content=email_body)

            else:
                setattr(user, 'status', 'rejected')
                email_body = ArtistApprovalEmail.REJECTED_EMAIL_BODY.replace('{name}', user.full_name)
                plain_email_body = ArtistApprovalEmail.PLAIN_REJECTED_EMAIL_BODY.replace('{name}', user.full_name)
                send_email = send_plain_email(user.email, ArtistApprovalEmail.EMAIL_SUBJECT, plain_email_body, False,
                                              is_html=True, html_content=email_body)

            log = {
                'email_type': EmailTypes.ARTIST_APPROVAL_EMAIL,
                'user_id': user.id,
                'email_from_name': None,
                'email_to': user.email,
                'email_subject': ArtistApprovalEmail.EMAIL_SUBJECT,
                'email_body': email_body
            }

            if send_email:
                log['status_code'] = send_email['status_code']
                log['message'] = send_email['body']

            EmailLog.log_to_db(**log)
        except Exception as e:
            return {
                       'status': 'error',
                       'message': 'Failed to send email. Please try again'
                   }, 500

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {
                       'status': 'error',
                       'message': 'failed update to database'
                   }, 422

        user_dump = UserSchema().dump(user).data
        user_dump.pop("password", None)
        user_dump.pop("email_logs", None)

        return {
            'status': 'success',
            'user': user_dump
        }


@api.route("/password")
class UpdatePasswordResource(Resource):
    method_decorators = [jwt_required]

    @api.expect(api.model('PasswordPostFields', {
        'password': fields.String(required=True, description='New Password'),
        'password_2': fields.String(required=True, description='Confirmed New Password'),
    }))
    def post(self):
        reset_password_fields = request.json
        password = reset_password_fields.get('password')
        password_2 = reset_password_fields.get('password_2')
        if not password == password_2:
            return {'error': 'Passwords do not match.'}, 400

        user = User.get(get_jwt_identity())
        user.update_password(password_2)
        try:
            db.session.commit()
            return {'error': None, 'msg': 'Password successfully updated.'}
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to save password in database update'}, 400


@api.route("/details")
@api.doc(parser=parser)
class GetUserDetails(Resource):
    method_decorators = [jwt_required]

    @api.response(200, 'Get User details successfully.', api.model('UserDetailsResponseModel', {
        'status': fields.String(description='status'),
        'user': fields.Nested(artist_response_fields, description='user details')
    }))
    def get(self):
        user = User.get(get_jwt_identity())

        user = UserSchema().dump(user).data

        return {
            'status': 'success',
            'user': user
        }


@api.route("/details/<string:user_id>")
class GetUserDetailsById(Resource):

    @api.response(200, 'Get User details By ID successfully.', api.model('UserDetailsByIdResponseModel', {
        'status': fields.String(description='status'),
        'user': fields.Nested(artist_response_fields, description='user details')
    }))
    def get(self, user_id):
        user = User.get(user_id)

        user = UserSchema().dump(user).data

        return {
            'status': 'success',
            'user': user
        }
