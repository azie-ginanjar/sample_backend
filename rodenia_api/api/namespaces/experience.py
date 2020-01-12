import base64
import datetime
import time
import uuid
from io import BytesIO

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restplus import Namespace, Resource, fields

from rodenia_api.commons.decorators import admin_required
from rodenia_api.commons.pagination import paginate
from rodenia_api.commons.schemas import BuyExperienceSchema, ExperienceSchema  , BuyExperienceSchema, \
    ArtistExperienceApplicationSchema
from rodenia_api.commons.util import generate_epoch_from_string_datetime, save_file_in_s3_by_file
from rodenia_api.constants import Categories, VALID_CATEGORY, EmailTypes, BuyExperienceEmail, ApplyExperienceEmail
from rodenia_api.extensions import db, sentry
from rodenia_api.models import Experience, User, ArtistExperienceApplication, EmailLog, BuyExperience
from rodenia_api.commons.email_utils_v2 import send_plain_email
import stripe
import os

api = Namespace('experience', description='Experience related operations')

parser = api.parser()
parser.add_argument('Authorization', type=str, location='headers')

create_experience_request_fields = api.model('CreateExperienceRequestModel', {
    'title': fields.String(required=True),
    'category': fields.String(required=False),
    'description': fields.String(required=True),
    'policy': fields.String(required=True),
    'guest_price': fields.Float(required=True),
    'artist_booking_price': fields.Float(required=True),
    'artist_slot': fields.Integer(required=True),
    'guest_slot': fields.Integer(required=True),
    'can_apply': fields.Boolean(required=True),
    'can_purchase': fields.Boolean(required=True),
    'potential_to_earn': fields.Float(required=True),
    'location': fields.String(required=True),
    'start_date': fields.String(required=True),
    'end_date': fields.String(required=True)
})

update_experience_request_fields = api.model('UpdateExperienceRequestModel', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=False),
    'category': fields.String(required=False),
    'description': fields.String(required=False),
    'policy': fields.String(required=False),
    'guest_price': fields.Float(required=False),
    'artist_booking_price': fields.Float(required=False),
    'artist_slot': fields.Integer(required=False),
    'guest_slot': fields.Integer(required=False),
    'can_apply': fields.Boolean(required=False),
    'can_purchase': fields.Boolean(required=False),
    'potential_to_earn': fields.Float(required=False),
    'location': fields.String(required=False),
    'start_date': fields.String(required=False),
    'end_date': fields.String(required=False)
})

experience_response_fields = api.model('CreateExperienceResponseModel', {
    'id': fields.Integer(),
    'title': fields.String(),
    'category': fields.String(),
    'description': fields.String(),
    'policy': fields.String(),
    'guest_price': fields.Float(),
    'artist_booking_price': fields.Float(),
    'artist_slot': fields.Integer(),
    'guest_slot': fields.Integer(),
    'can_apply': fields.Boolean(),
    'can_purchase': fields.Boolean(),
    'potential_to_earn': fields.Float(),
    'location': fields.String(),
    'start_date': fields.String(),
    'epoch_start_date': fields.Integer(),
    'end_date': fields.String(),
    'epoch_end_date': fields.Integer(),
    'created_by': fields.String(),
    'created_at': fields.String(),
    'epoch_created_at': fields.Integer()
})

experience_data_response_fields = api.model('ExperienceDataResponse', {
    'total': fields.Integer(),
    'pages': fields.Integer(),
    "next": fields.String(),
    "prev": fields.String(),
    "results": fields.List(fields.Nested(experience_response_fields))
})

buy_experience_response_fields = api.model('BuyExperienceResponseModel', {
    'id': fields.Integer(description='buy experience id'),
    'experience_id': fields.Integer(description='experience id'),
    'email': fields.String(description='email'),
    'number_of_slots': fields.Integer(description='number of slots bought'),
    'created_at': fields.String(),
    'epoch_created_at': fields.Integer()
})

apply_experience_response_fields = api.model('ApplyExperienceResponseModel', {
    'id': fields.Integer(description='buy experience id'),
    'experience_id': fields.Integer(description='experience id'),
    'user_id': fields.Integer(description='user id'),
    'images': fields.List(fields.String(description='image')),
    'about': fields.String(description="about artist"),
    'created_at': fields.String(),
    'epoch_created_at': fields.Integer()
})


@api.route("/")
@api.doc(parser=parser)
class ExperienceResource(Resource):

    @admin_required
    @api.expect(create_experience_request_fields, validate=True)
    @api.response(201, 'Create experience successfully.', api.model('CreateExperienceReponseModel', {
        'status': fields.String(description='status'),
        'experience': fields.Nested(experience_response_fields, description='experience data')
    }))
    def post(self):
        experience_data = request.json

        experience = Experience(
            category=Categories.MUSIC
        )

        for key, value in experience_data.items():
            if key == 'category' and value.lower() not in VALID_CATEGORY:
                return {
                    'status': 'error',
                    'message': 'invalid category'
                }, 400

            setattr(experience, key, value)

        user = User.get(get_jwt_identity())

        setattr(experience, 'epoch_start_date', generate_epoch_from_string_datetime(experience_data['start_date']))
        setattr(experience, 'epoch_end_date', generate_epoch_from_string_datetime(experience_data['end_date']))
        setattr(experience, 'created_by', user.id)

        db.session.add(experience)

        try:
            db.session.commit()

            created_by = experience.user.full_name
            experience = ExperienceSchema().dump(experience).data
            experience['created_by'] = created_by
            return {
                       'status': 'success',
                       'experience': experience
                   }, 201
        except Exception as e:
            db.session.rollback()
            return {
                       'status': 'error',
                       'message': 'failed save to database'
                   }, 422

    @admin_required
    @api.expect(update_experience_request_fields, validate=True)
    @api.response(200, 'Create experience successfully.', api.model('EditExperienceResponseModel', {
        'status': fields.String(description='status'),
        'experience': fields.Nested(experience_response_fields, description='experience data')
    }))
    def put(self):
        experience_data = request.json

        experience_id = experience_data['id']

        experience = Experience.query.filter(
            Experience.id == experience_id
        ).first()

        if not experience:
            return {
                       'status': 'error',
                       'message': 'experience not found.'
                   }, 400

        for key, value in experience_data.items():
            if key == 'category' and value.lower() not in VALID_CATEGORY:
                return {
                    'status': 'error',
                    'message': 'invalid category'
                }, 400

            if key != id:
                setattr(experience, key, value)
                if key == 'start_date' or key == 'end_date':
                    setattr(experience, 'epoch_{}'.format(key), generate_epoch_from_string_datetime(value))

        user = User.get(get_jwt_identity())

        setattr(experience, 'last_updated_at', datetime.datetime.utcnow().isoformat())
        setattr(experience, 'epoch_last_updated_at', int(time.time()))
        setattr(experience, 'last_updated_by', user.id)

        try:
            db.session.commit()

            created_by = experience.user.full_name
            experience = ExperienceSchema().dump(experience).data
            experience['created_by'] = created_by
            return {
                'status': 'success',
                'experience': experience
            }
        except Exception as e:
            db.session.rollback()
            return {
                       'status': 'error',
                       'message': 'failed update to database'
                   }, 422

    @admin_required
    @api.expect(api.model('DeleteExperienceFields', {
        'experience_id': fields.Integer(required=True, description='Experience Id')
    }), validate=True)
    @api.response(200, 'Experience successfully deleted.', api.model('DeleteExperienceResponseModel', {
        'status': fields.String(description='status'),
        'id': fields.Nested(experience_response_fields, description='experience id')
    }))
    def delete(self):

        request_data = request.get_json(silent=True)
        experience_id = request_data.get("experience_id")
        experience = Experience.query.filter(
            Experience.id == experience_id
        ).first()

        if not experience:
            return {
                       'status': 'error',
                       'message': 'experience not found.'
                   }, 400

        db.session.delete(experience)
        try:
            db.session.commit()

            experience = ExperienceSchema().dump(experience).data

            return {
                'status': 'success',
                'experience': experience
            }
        except Exception as e:
            db.session.rollback()
            return {
                       'status': 'error',
                       'message': "database error: failed to delete experience"
                   }, 422

    query_parser = api.parser()
    query_parser.add_argument('category', required=False, location='args', type=str,
                              help='all, music(default), dance, theatre, food')
    query_parser.add_argument('can_apply', required=False, location='args', type=str)
    query_parser.add_argument('page', required=False, type=int, help='by default equal to 1')
    query_parser.add_argument('page_size', required=False, type=int, help='by default equal to 10')

    @api.expect(query_parser, validate=True)
    @api.response(200, 'Get Experiences list successfully.', api.model('ExperienceResponseModel', {
        'status': fields.String(description='status'),
        'data': fields.Nested(experience_data_response_fields, description='experiences data')
    }))
    def get(self):
        category = request.args.get('category', Categories.MUSIC).lower()
        can_apply = request.args.get('can_apply')

        experiences = Experience.query.filter(
            Experience.category == category
        ).order_by(
            Experience.id.desc()
        )

        if can_apply:
            experiences = experiences.filter(
                Experience.can_apply == can_apply
            )

        schema = ExperienceSchema(many=True)
        data = paginate(experiences, schema)

        return {
            'status': 'success',
            'data': data
        }


@api.route("/<string:experience_id>")
class GetExperienceDetails(Resource):

    @api.response(200, 'Get Experiences details successfully.', api.model('ExperienceDetailsResponseModel', {
        'status': fields.String(description='status'),
        'experience': fields.Nested(experience_response_fields, description='experience details')
    }))
    def get(self, experience_id):
        experience = Experience.query.filter(
            Experience.id == experience_id
        ).first()

        guest_slot_left = experience.guest_slot
        artist_slot_left = experience.artist_slot - len(experience.artist_applications)

        for buy_experience in experience.buy_experiences:
            guest_slot_left -= buy_experience.number_of_slots

        experience = ExperienceSchema().dump(experience).data

        experience['guest_slot_left'] = guest_slot_left
        experience['artist_slot_left'] = artist_slot_left
        return {
            'status': 'success',
            'experience': experience
        }


@api.route("/buy")
class BuyExperienceResource(Resource):

    @api.expect(api.model('BuyExperienceRequestModel', {
        'experience_id': fields.Integer(required=True),
        'email': fields.String(required=True),
        'number_of_slots': fields.Integer(required=True),
        'stripe_token': fields.String(required=True)
    }), validate=True)
    @api.response(201, 'Buy Experience successfully.', api.model('BuyExperienceResponseModelData', {
        'status': fields.String(description='status'),
        'buy_experience': fields.Nested(buy_experience_response_fields, description="buy experience details")
    }))
    def post(self):
        experience_data = request.json

        experience_id = experience_data['experience_id']
        email = experience_data['email']
        number_of_slots = experience_data['number_of_slots']
        stripe_token = experience_data['stripe_token']

        experience = Experience.query.filter(
            Experience.id == experience_id
        ).first()

        if not experience.can_purchase:
            return {
                'status': 'failed',
                'message': 'could not purchase ticket, can_purchase = false'
            }, 403

        guest_slot_left = experience.guest_slot

        for buy_experience in experience.buy_experiences:
            guest_slot_left -= buy_experience.number_of_slots

        if number_of_slots > guest_slot_left:
            return {
                'status': 'error',
                'message': 'Not enough guest tickets remaining to fulfill this order.'
            }, 400

        # Trigger experience buying flow

        # STEP 1: Generate Stripe Charge
        stripe.api_key = os.getenv('STRIPE_API_KEY')
        try:
            charge = stripe.Charge.create(
                amount=int(experience.guest_price * 100),
                currency='usd',
                description='Rodenia Experience',
                source=stripe_token,
            )
        except Exception as e:
            return {
                'status': 'error',
                'message': 'Failed to purchase experience due to Stripe charge issue.'
            }, 500

        # STEP 2: Send followup email
        try:
            email_body = BuyExperienceEmail.EMAIL_BODY.replace('{experience_name}', experience.title)\
                .replace('{slot}', str(number_of_slots)).replace('{address}', experience.location)

            plain_email_body = BuyExperienceEmail.PLAIN_EMAIL_BODY.replace('{experience_name}', experience.title)\
                .replace('{slot}', str(number_of_slots)).replace('{address}', experience.location)

            send_email = send_plain_email(
                email, 
                BuyExperienceEmail.EMAIL_SUBJECT,
                plain_email_body,
                False,
                is_html=True,
                html_content=email_body
            )

            log = {
                'email_type': EmailTypes.BUY_EXPERIENCE_EMAIL,
                'user_id': None,
                'email_from_name': None,
                'email_to': email,
                'email_subject': BuyExperienceEmail.EMAIL_SUBJECT,
                'email_body': email_body
            }

            if send_email:
                log['status_code'] = send_email['status_code']
                log['message'] = send_email['body']

            EmailLog.log_to_db(**log)
        except Exception as e:
            sentry.captureException()

        # STEP 3: Create record in DB for auditing/tracking purposes.
        buy_experience = BuyExperience(
            experience_id=experience_id,
            email=email,
            number_of_slots=number_of_slots
        )

        db.session.add(buy_experience)

        try:
            db.session.commit()

            buy_experience = BuyExperienceSchema().dump(buy_experience).data
            return {
                'status': 'success',
                'buy_experience': buy_experience
            }, 201
        except Exception as e:
            db.session.rollback()
            sentry.captureException()
            return {
                'status': 'error',
                'message': 'failed record data to db'
            }, 422


@api.route("/apply")
@api.doc(parser=parser)
class ApplyExperience(Resource):
    method_decorators = [jwt_required]

    @api.expect(api.model('ApplyExperienceRequestModel', {
        'experience_id': fields.Integer(required=True),
        'images': fields.List(fields.String(required=True), required=False),
        'about': fields.String(required=True)
    }), validate=True)
    @api.response(201, 'Apply Experience successfully.', api.model('ApplyExperienceResponseModelData', {
        'status': fields.String(description='status'),
        'artist_application': fields.Nested(apply_experience_response_fields, description='experience details')
    }))
    def post(self):
        experience_data = request.json

        experience_id = experience_data['experience_id']
        user_id = get_jwt_identity()
        about = experience_data['about']

        experience = Experience.query.filter(
            Experience.id == experience_id
        ).first()

        user = User.get(user_id)

        if not experience:
            return {
                       'status': 'failed',
                       'message': 'experience not found'
                   }, 400

        if not experience.can_apply:
            return {
                'status': 'failed',
                'message': 'could not apply for experience, can_apply = false'
            }, 403

        artist_slot_left = experience.artist_slot - len(experience.artist_applications)

        if artist_slot_left <= 0:
            return {
               'status': 'error',
               'message': 'not enough slot'
            }, 400

        # save images to s3
        images_url = []

        if 'images' in experience_data:
            images = experience_data['images']
            for image in images:
                image_ext = image.split(';base64')[0].replace('data:image/', '')

                image = image.split('base64,')[1]

                file = BytesIO(base64.b64decode(image))

                filename = '{}.{}'.format(str(uuid.uuid4()), image_ext)

                is_save_image_success = save_file_in_s3_by_file('rodenia-images', file, filename)

                #  if failed to upload just neglected it
                if is_save_image_success:
                    images_url.append('https://rodenia-images.s3.us-east-2.amazonaws.com/{}'.format(filename))

        try:
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

                email_body = ApplyExperienceEmail.EMAIL_BODY.replace('{artist_name}', user.full_name)\
                    .replace('{experience_name}', experience.title)

                plain_email_body = ApplyExperienceEmail.PLAIN_EMAIL_BODY.replace('{artist_name}', user.full_name) \
                    .replace('{experience_name}', experience.title)

                send_email = send_plain_email(
                    admin_emails,
                    ApplyExperienceEmail.EMAIL_SUBJECT,
                    plain_email_body,
                    is_multiple,
                    is_html=True,
                    html_content=email_body
                )

                log = {
                    'email_type': EmailTypes.APPLY_EXPERIENCE_EMAIL,
                    'user_id': user_id,
                    'email_from_name': None,
                    'email_to': str(admin_emails),
                    'email_subject': ApplyExperienceEmail.EMAIL_SUBJECT,
                    'email_body': email_body
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

        artist_application = ArtistExperienceApplication(
            experience_id=experience_id,
            user_id=user_id,
            images=images_url,
            about=about
        )

        db.session.add(artist_application)

        try:
            db.session.commit()

            artist_application = ArtistExperienceApplicationSchema().dump(artist_application).data
            return {
                       'status': 'success',
                       'artist_application': artist_application
                   }, 201
        except Exception as e:
            db.session.rollback()
            return {
                       'status': 'error',
                       'message': 'failed record data to db'
                   }, 422
