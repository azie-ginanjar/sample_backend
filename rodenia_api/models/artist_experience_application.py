import datetime
import time

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy.sql import sqltypes

from rodenia_api.extensions import db
from rodenia_api.models import User


class ArtistExperienceApplication(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    experience_id = db.Column(db.Integer(), ForeignKey('experience.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, ForeignKey(User.id, ondelete='CASCADE'))
    images = db.Column(postgresql.ARRAY(sqltypes.Text))
    about = db.Column(db.String())

    __table_args__ = (
        UniqueConstraint('user_id', 'experience_id', name='unique_user_experience'),
    )

    experience = relationship(
        'Experience',
        backref='artist_applications'
    )

    def __init__(self, **kwargs):
        super(ArtistExperienceApplication, self).__init__(**kwargs)

        self.created_at = datetime.datetime.utcnow().isoformat()
        self.epoch_created_at = int(time.time())
