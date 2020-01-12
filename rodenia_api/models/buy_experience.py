import datetime
import time

from sqlalchemy import ForeignKey

from rodenia_api.extensions import db


class BuyExperience(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    experience_id = db.Column(db.Integer(), ForeignKey('experience.id', ondelete='CASCADE'))
    number_of_slots = db.Column(db.Integer())
    email = db.Column(db.String())
    created_at = db.Column(db.String())
    epoch_created_at = db.Column(db.Integer())

    def __init__(self, **kwargs):
        super(BuyExperience, self).__init__(**kwargs)

        self.created_at = datetime.datetime.utcnow().isoformat()
        self.epoch_created_at = int(time.time())
