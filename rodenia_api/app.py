from flask import Flask
from flask_cors import CORS
from rodenia_api import auth, api
from rodenia_api.extensions import db, jwt, migrate, sentry
import os

PRODUCTION = 'production'
STAGING = 'staging'


def create_app(testing=False, cli=False):
    """Application factory, used to create application
    """
    app = Flask('rodenia_api')

    configure_app(app, testing)
    configure_extensions(app, cli)
    register_blueprints(app)

    return app


def configure_app(app, testing=False):
    environment = os.environ.get('ENVIRONMENT')

    # default configuration
    app.config.from_object('rodenia_api.config')
    if testing is True:
        # override with testing config
        app.config.from_object('rodenia_api.configtest')
    else:
        if environment == PRODUCTION:
            app.config.from_object('rodenia_api.configprod')
        elif environment == STAGING:
            app.config.from_object('rodenia_api.configstaging')


def configure_extensions(app, cli):
    """configure flask extensions
    """
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    if cli is True:
        migrate.init_app(app, db)

    # HACK here: Sentry for some reason can't be configured without the DSN variable
    sentry.init_app(app, dsn=app.config.get('SENTRY_DSN'))


def register_blueprints(app):
    """register all blueprints for application
    """
    app.register_blueprint(auth.views.blueprint)
    app.register_blueprint(api.views.blueprint)
