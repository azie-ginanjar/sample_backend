import datetime
import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from rodenia_api.extensions import db


class Experience(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    category = db.Column(db.String())
    description = db.Column(db.String())
    policy = db.Column(db.String())
    guest_price = db.Column(db.Float())
    artist_booking_price = db.Column(db.Float())
    guest_slot = db.Column(db.Integer())
    artist_slot = db.Column(db.Integer())
    start_date = db.Column(db.String())
    epoch_start_date = db.Column(db.Integer())
    end_date = db.Column(db.String())
    epoch_end_date = db.Column(db.Integer())
    location = db.Column(db.String())
    can_apply = db.Column(db.Boolean())
    can_purchase = db.Column(db.Boolean())
    potential_to_earn = db.Column(db.Float())
    created_by = db.Column(db.Integer(), ForeignKey('user_v2.id', ondelete='CASCADE'))
    created_at = db.Column(db.String())
    epoch_created_at = db.Column(db.Integer())
    last_updated_at = db.Column(db.String())
    epoch_last_updated_at = db.Column(db.Integer())
    last_updated_by = db.Column(db.String())

    buy_experiences = relationship(
        'BuyExperience',
        backref='experience',
        cascade="all,delete, delete-orphan"
    )

    def __init__(self, **kwargs):
        super(Experience, self).__init__(**kwargs)

        self.created_at = datetime.datetime.utcnow().isoformat()
        self.epoch_created_at = int(time.time())
