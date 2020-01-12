import base64
import datetime
import traceback
import uuid
from io import BytesIO

from flask import request, current_app
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_refresh_token_required,
    create_access_token,
    create_refresh_token,
)
from flask_restplus import Namespace, Resource, fields
from rq import Queue

from rodenia_api.commons.decorators import admin_required
from rodenia_api.commons.email_utils_v2 import send_plain_email
from rodenia_api.commons.schemas import UserSchema
from rodenia_api.commons.util import save_file_in_s3_by_file
from rodenia_api.constants import NewSignedUpEmail, EmailTypes
from rodenia_api.extensions import (
    db,
    redis_conn,
    pwd_context)
from rodenia_api.models import User, ResetToken, EmailLog

q = Queue('default', connection=redis_conn)

api = Namespace('', description='Registration/Login/API Authorization related operations')

registration_artist_resource_fields = api.model('ArtistRegistrationDetails', {
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password'),
    'full_name': fields.String(required=True, description='Full Name'),
    'professional_talent': fields.String(required=True, description='Professional Talent'),
    'city': fields.String(required=True, description='City'),
    'state': fields.String(required=True, description='State'),
    'zipcode': fields.String(required=True, description='Zip Code'),
    'self_description': fields.String(required=True, description='Self description'),
    'facebook': fields.String(required=False, description='Facebook'),
    'instagram': fields.String(required=False, description='Instagram'),
    'twitter': fields.String(required=False, description='Twitter'),
    'youtube': fields.String(required=False, description='Youtube'),
    'pinterest': fields.String(required=False, description='Pinterest'),
    'image': fields.String(required=False, description='Image')
})

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

login_resource_fields = api.model('LoginDetails', {
    'email': fields.String(required=True),
    'password': fields.String(required=True),
})

reset_password_resource_resource_fields = api.model('ResetPasswordFields', {
    'token_str': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password'),
    'password_2': fields.String(required=True, description='Stripe Token')
})

parser = api.parser()
parser.add_argument('Authorization', type=str, location='headers')


@api.route('/registration/artist')
class RegistrationArtistResource(Resource):
    method_decorators = []

    @api.expect(registration_artist_resource_fields, validate=True)
    @api.response(201, 'Artist successfully registered.', api.model('RegisterArtistReponseModel', {
        'status': fields.String(description='status'),
        'user': fields.Nested(artist_response_fields)
    }))
    @api.response(400, 'Invalid payload parameter', api.model('CampaignCreateInvalidPayloadReponseModel', {
        'error': fields.String(description='error message')
    }))
    @api.response(422, 'Failed save to DB', api.model('CampaignCreateFailedSaveDbReponseModel', {
        'message': fields.String(description='message'),
        'status': fields.String(description='status')
    }))
    def post(self):
        request_data = request.json

        user = User.find_user_by_email(request_data['email'])

        if user:
            return {
                'status': 'error',
                'message': 'email already registered'
            }, 422

        user = User(
            role='artist',
            status='pending',
            password=request_data['password']
        )

        for key, value in request_data.items():
            if key != 'password' and key != 'image':
                setattr(user, key, value)

        if 'image' in request_data:
            image = request_data['image']
            image_ext = image.split(';base64')[0].replace('data:image/', '')

            image_base64 = image.split('base64,')

            if len(image_base64) < 2:
                return {
                           'status': 'error',
                           'message': 'invalid image file'
                       }, 400

            image = image.split('base64,')[1]

            file = BytesIO(base64.b64decode(image))

            filename = '{}.{}'.format(str(uuid.uuid4()), image_ext)

            is_save_image_success = save_file_in_s3_by_file('rodenia-images', file, filename)

            if not is_save_image_success:
                return {
                           'status': 'error',
                           'message': 'failed save to aws'
                       }, 422

            setattr(user, 'image', 'https://rodenia-images.s3.us-east-2.amazonaws.com/{}'.format(filename))

        try:
            # get admins data
            admin = User.query.filter(
                User.role == 'admin'
            ).all()
            admin_emails = [a.email for a in admin]

            if admin_emails:
                is_multiple = False
                if len(admin_emails) > 1:
                    is_multiple = True
                else:
                    admin_emails = admin_emails[0]

                send_email = send_plain_email(admin_emails, NewSignedUpEmail.EMAIL_SUBJECT,
                                              NewSignedUpEmail.PLAIN_EMAIL_BODY,
                                              is_multiple, is_html=True, html_content=NewSignedUpEmail.EMAIL_BODY)

                log = {
                    'email_type': EmailTypes.NEW_SIGNED_UP_EMAIL,
                    'user_id': user.id,
                    'email_from_name': None,
                    'email_to': str(admin_emails),
                    'email_subject': NewSignedUpEmail.EMAIL_SUBJECT,
                    'email_body': NewSignedUpEmail.EMAIL_BODY
                }

                if send_email:
                    log['status_code'] = send_email['status_code']
                    log['message'] = send_email['body']

                EmailLog.log_to_db(**log)

        except Exception as e:
            return {
                       'status': 'error',
                       'message': 'Failed to send in application to admin for approval. Please try again'
                   }, 500

        db.session.add(user)

        try:
            db.session.commit()

            user_dump = UserSchema().dump(user).data
            user_dump.pop("password", None)
            user_dump.pop("email_logs", None)

            return {
                       'status': 'success',
                       'user': user_dump
                   }, 201
        except Exception as e:
            print(str(e))
            db.session.rollback()
            return {
                       'status': 'error',
                       'message': 'failed save to database'
                   }, 422


@api.route('/login')
class LoginResource(Resource):
    method_decorators = []

    @api.expect(login_resource_fields, validate=True)
    @api.response(200, 'Logged in successfully.', api.model('LoginReponseModel', {
        'access_token': fields.String(description='access token'),
        'refresh_token': fields.String(description='refresh token'),
        'user': fields.Nested(artist_response_fields)
    }))
    @api.response(400, 'Invalid payload parameter', api.model('CampaignCreateInvalidPayloadReponseModel', {
        'error': fields.String(description='error message')
    }))
    def post(self):
        """Authenticate user and return token"""
        if not request.is_json:
            return {'error': 'Missing JSON in request'}

        email = request.json.get('email', None)
        password = request.json.get('password', None)

        user = User.find_user_by_email(email.lower())

        if user is None or not pwd_context.verify(password, user.password):
            return {'error': 'Invalid email or password'}, 401

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        user_dump = UserSchema().dump(user).data
        user_dump.pop("password", None)
        user_dump.pop("email_logs", None)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user_dump
        }


@api.route('/admin_login')
@api.doc(parser=parser)
class AdminLoginResource(Resource):
    method_decorators = [admin_required]

    @api.expect(api.model('AdminLoginDetails', {
        'username': fields.String(required=True),
    }), validate=True)
    def post(self):

        """Authenticate user and return token"""
        if not request.is_json:
            return {'error': 'Missing JSON in request'}

        username = request.json.get('username', None)
        if not username:
            return {'error': 'Missing username'}

        user = User.find_user_by_username(username.lower())
        if user is None:
            return {'error': 'Bad credentials'}

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        ret = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return ret


@api.route('/refresh')
class RefreshTokenResource(Resource):
    method_decorators = [jwt_refresh_token_required]

    def post(self):
        """Refresh token for user to maintain user identity"""
        current_user = get_jwt_identity()
        ret = {
            'access_token': create_access_token(identity=current_user)
        }
        return ret


@api.route('/generate_reset_token')
class ResetTokenResource(Resource):
    method_decorators = []

    @api.expect(api.model('GenerateResetTokenPostResourceFields', {
        'email': fields.String(required=True, description='Required if method is email')
    }))
    def post(self):
        """
        Start of password recovery.
        System generates reset password token and sends it to the email user specified.
        """

        email = request.json.get('email')
        if not email:
            return {'error': 'No email in request.'}

        user = User.find_user_by_email(email)
        if not user:
            return {'error': 'No user found for this email.'}

        ResetToken.query.filter_by(user_id=user.id).delete()
        reset_token = ResetToken(user_id=user.id, token_str=str(uuid.uuid4()))
        db.session.add(reset_token)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            return {'error': None, 'msg': 'Failed to save reset token to database.'}

        if not current_app.testing:
            # @TODO actually send the email using SendGrid
            return {'error': None, 'msg': 'Successfully sent email.'}


@api.route('/reset_password')
class ResetPasswordResource(Resource):
    method_decorators = []

    @api.expect(reset_password_resource_resource_fields)
    def post(self):
        """
        Second and final step for resetting password. Grabs the token correct token,
        and finds the corresponding user and updates the password.
        """
        reset_password_fields = request.json
        token_str = reset_password_fields['token_str']
        password = reset_password_fields['password']
        password_2 = reset_password_fields['password_2']
        reset_token = ResetToken.query.filter_by(token_str=token_str).first()
        if not password == password_2:
            return {'error': 'Passwords do not match.'}

        if not reset_token:
            return {'error': 'Reset token not found.'}

        if reset_token.expiration_date < datetime.datetime.utcnow().isoformat():
            return {'error': 'Reset token has already expired.'}

        user = User.query.filter_by(id=reset_token.user_id).first()
        user.update_password(password_2)
        try:
            db.session.commit()
            return {'error': None, 'msg': 'Password successfully updated.'}
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to save password in database update'}
