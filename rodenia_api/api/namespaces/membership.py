from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restplus import Namespace, Resource, fields
from flask import request
from rodenia_api.libraries.membership_lib import membership_utils
from rodenia_api.extensions import db
from rodenia_api.models import User
import json

api = Namespace('membership', description='Membership related operations')
update_billing_input_fields = api.model('Listing Defaults', {
    'stripeToken': fields.String(
        required=True,
        description='Stripe Token for updating the billing',
    )
})


@api.route('/')
class MembershipResource(Resource):
    method_decorators = [jwt_required]

    def get(self):
        """ Gets the current membership data for the user. """
        user_id = get_jwt_identity()
        current_user = User.get(user_id)
        customer_id = current_user.customer_id

        try:
            data = membership_utils.get_membership_data(customer_id)
        except Exception as e:
            return {
                'error': 'Failed to get membership data: {}.'.format(e)
            }

        return {'data': json.dumps(data, indent=4)}

    def delete(self):
        """ Cancels the current membership for the user. """
        user_id = get_jwt_identity()
        current_user = User.get(user_id)
        user_object_id = current_user.id
        customer_id = current_user.customer_id
        try:
            membership_utils.cancel_membership(user_object_id, customer_id)
        except Exception as e:
            return {
                'error': 'Failed to delete membership: {}'.format(e)
            }

        current_user.cancel_membership()
        try:
            db.session.commit()
            return {
                'error': None,
                "msg": "Successfully deleted membership."
            }
        except Exception as e:
            db.session.rollback()
            return {
                'error': 'Failed to delete membership: {}'.format(e)
            }

    def post(self):
        """ Restarts the membership for the current user. """
        user_id = get_jwt_identity()
        current_user = User.get(user_id)
        customer_id = current_user.customer_id
        try:
            membership_utils.restart_membership(user_id, customer_id)
        except Exception as e:
            return {
                'error': 'Failed to restart membership: {}'.format(e)
            }

        current_user.restart_membership()
        try:
            db.session.commit()
            return {
                'error': None,
                'msg': 'Successfully restarted membership.'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'error': 'Failed to restarted membership: {}'.format(e)
            }


@api.route('/billing')
class BillingResource(Resource):
    method_decorators = [jwt_required]

    @api.expect(update_billing_input_fields)
    def post(self):
        """ Updates the billing method for the current user. """
        stripe_token = request.get_json().get('stripeToken')

        if not stripe_token:
            return {
                'error': 'Failed to update billing because we did not receive a stripe token.'
            }

        user_id = get_jwt_identity()
        current_user = User.get(user_id)
        customer_id = current_user.customer_id
        try:
            return membership_utils.update_billing(customer_id, stripe_token)
        except Exception as e:
            return {
                'error': 'Failed to update billing: {}'.format(e)
            }
