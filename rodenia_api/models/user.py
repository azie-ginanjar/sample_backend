import datetime
import time

from sqlalchemy import func, UniqueConstraint
from sqlalchemy.orm import relationship

from rodenia_api.extensions import db, pwd_context


class User(db.Model):
    __tablename__ = "user_v2"
    id = db.Column(db.Integer(), primary_key=True)
    role = db.Column(db.String())
    full_name = db.Column(db.String())
    professional_talent = db.Column(db.String())
    email = db.Column(db.String())
    password = db.Column(db.String())
    city = db.Column(db.String())
    state = db.Column(db.String())
    zipcode = db.Column(db.String())
    self_description = db.Column(db.String())
    facebook = db.Column(db.String())
    instagram = db.Column(db.String())
    twitter = db.Column(db.String())
    youtube = db.Column(db.String())
    pinterest = db.Column(db.String())
    image = db.Column(db.String())
    created_at = db.Column(db.String())
    epoch_created_at = db.Column(db.Integer())
    status = db.Column(db.String())

    __table_args__ = (
        UniqueConstraint('email', name='unique_email'),
    )

    email_logs = relationship(
        'EmailLog',
        backref='user',
        cascade="all,delete, delete-orphan"
    )

    experiences = relationship(
        'Experience',
        backref='user',
        cascade="all,delete, delete-orphan"
    )

    artist_applications = relationship(
        'ArtistExperienceApplication',
        backref='user',
        cascade="all,delete, delete-orphan"
    )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.password = pwd_context.hash(kwargs.get('password'))
        self.created_at = datetime.datetime.utcnow().isoformat()
        self.epoch_created_at = int(time.time())

    def update_password(self, password):
        self.password = pwd_context.hash(password)

    def activate_user(self):
        self.is_active = True

    @staticmethod
    def get(user_id):
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def find_user_by_email(email):
        return User.query.filter(func.lower(User.email) == func.lower(email)).first()

    @staticmethod
    def get_users():
        return User.query.all()

    @staticmethod
    def get_active_users():
        return User.query.filter_by(is_active=True)

