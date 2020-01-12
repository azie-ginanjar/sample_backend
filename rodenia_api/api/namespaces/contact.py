from flask import request
from flask_restplus import Namespace, fields, Resource

from rodenia_api.commons.email_utils_v2 import send_plain_email
from rodenia_api.constants import EmailTypes, NewSignedUpEmail, ArtistApprovalEmail, BuyExperienceEmail, \
    ApplyExperienceEmail
from rodenia_api.models import User, EmailLog

api = Namespace('contact', description='Experience related operations')


@api.route("/")
class ContactResource(Resource):

    @api.expect(api.model('ContactRequestModel', {
        'email': fields.String(required=True),
        'message': fields.String(required=True)
    }), validate=True)
    @api.response(200, 'Contact sent successfully.', api.model('ContactResponseModel', {
        'status': fields.String(description='status')
    }))
    def post(self):
        contact_data = request.json

        email = contact_data['email']
        message = contact_data['message']

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

                send_email = send_plain_email(
                    admin_emails,
                    "New contact from rodenia",
                    message,
                    is_multiple,
                    email
                )

                log = {
                    'email_type': EmailTypes.CONTACT_EMAIL,
                    'user_id': None,
                    'email_from_name': email,
                    'email_to': str(admin_emails),
                    'email_subject': "New contact from rodenia",
                    'email_body':message,
                    'status_code': send_email["status_code"],
                    'message': send_email['body']
                }

                EmailLog.log_to_db(**log)

            return {
                "status": "success"
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': 'Failed to send email'
            }, 500


@api.route("/fake")
class EmailResource(Resource):

    @api.expect(api.model('FakeEmailRequestModel', {
        'email': fields.String(required=True),
        'template_type': fields.String(required=True)
    }), validate=True)
    @api.response(200, 'Fake Email sent successfully.', api.model('FakeEmailResponseModel', {
        'status': fields.String(description='status')
    }))
    def post(self):
        contact_data = request.json

        email = contact_data['email']
        template_type = contact_data['template_type']

        if template_type.lower() == EmailTypes.NEW_SIGNED_UP_EMAIL:
            subject = NewSignedUpEmail.EMAIL_SUBJECT
            body = NewSignedUpEmail.EMAIL_BODY
            plain_body = NewSignedUpEmail.PLAIN_EMAIL_BODY
        elif template_type.lower() == 'artist_rejection_email':
            subject = ArtistApprovalEmail.EMAIL_SUBJECT
            plain_body = ArtistApprovalEmail.PLAIN_REJECTED_EMAIL_BODY
            body = ArtistApprovalEmail.REJECTED_EMAIL_BODY
        elif template_type.lower() == 'artist_approval_email':
            subject = ArtistApprovalEmail.EMAIL_SUBJECT
            body = ArtistApprovalEmail.APPROVED_EMAIL_BODY
            plain_body = ArtistApprovalEmail.PLAIN_APPROVED_EMAIL_BODY
        elif template_type.lower() == EmailTypes.BUY_EXPERIENCE_EMAIL:
            subject = BuyExperienceEmail.EMAIL_SUBJECT
            body = BuyExperienceEmail.EMAIL_BODY
            plain_body = BuyExperienceEmail.PLAIN_EMAIL_BODY
        elif template_type.lower() == EmailTypes.APPLY_EXPERIENCE_EMAIL:
            subject = ApplyExperienceEmail.EMAIL_SUBJECT
            body = ApplyExperienceEmail.EMAIL_BODY
            plain_body = ApplyExperienceEmail.PLAIN_EMAIL_BODY
        else:
            return {
                       'status': 'error',
                       'message': 'Invalid email type'
                   }, 400

        try:
            send_email = send_plain_email(
                email,
                subject,
                plain_body,
                False,
                is_html=True,
                html_content=body
            )

            return {
                "status": "success"
            }
        except Exception as e:
            print(str(e))
            return {
                       'status': 'error',
                       'message': 'Failed to send email'
                   }, 500
