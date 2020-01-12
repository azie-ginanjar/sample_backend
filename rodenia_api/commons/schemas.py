from rodenia_api.extensions import ma, db
from rodenia_api.models import (
    User,
    Experience, BuyExperience, ArtistExperienceApplication)


class BuyExperienceSchema(ma.ModelSchema):
    class Meta:
        model = BuyExperience
        sqla_session = db.session


class ArtistApplicationSchema(ma.ModelSchema):
    class Meta:
        model = ArtistExperienceApplication
        sqla_session = db.session


class ExperienceSchema(ma.ModelSchema):
    class Meta:
        model = Experience
        sqla_session = db.session

    buy_experiences = ma.Nested(BuyExperienceSchema, many=True)
    artist_applications = ma.Nested(ArtistApplicationSchema, many=True)


class ArtistExperienceApplicationSchema(ma.ModelSchema):
    class Meta:
        model = ArtistExperienceApplication
        sqla_session = db.session

    experience = ma.Nested(ExperienceSchema, many=False)


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        sqla_session = db.session

    artist_applications = ma.Nested(ArtistExperienceApplicationSchema, many=True)
