import datetime

from sqlalchemy import ForeignKey

from rodenia_api.extensions import db

EXPIRATION_MINUTES = 15


class ResetToken(db.Model):
    user_id = db.Column(db.Integer(), ForeignKey('user_v2.id', ondelete='CASCADE'), primary_key=True)
    token_str = db.Column(db.String())
    expiration_date = db.Column(db.String())

    def __init__(self, user_id, token_str):
        self.user_id = user_id
        self.token_str = token_str
        expiration_date = datetime.datetime.utcnow() + datetime.timedelta(minutes=EXPIRATION_MINUTES)
        self.expiration_date = expiration_date.isoformat()
