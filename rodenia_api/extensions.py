"""Extensions registry

All extensions here are used as singletons and
initialized in application factory
"""
from flask_sqlalchemy import SQLAlchemy
from passlib.context import CryptContext
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from raven.contrib.flask import Sentry
import os
import redis

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
migrate = Migrate(compare_type=True)
pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
sentry = Sentry()
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis_conn = redis.from_url(redis_url)
