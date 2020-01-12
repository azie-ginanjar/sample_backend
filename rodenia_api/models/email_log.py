import datetime
import time

from sqlalchemy import ForeignKey

from rodenia_api.extensions import db


class EmailLog(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email_type = db.Column(db.String())
    user_id = db.Column(db.Integer(), ForeignKey('user_v2.id', ondelete='CASCADE'))
    email_from_name = db.Column(db.String())
    email_to = db.Column(db.String())
    email_subject = db.Column(db.String())
    email_body = db.Column(db.String())
    status_code = db.Column(db.Integer())
    message = db.Column(db.String(), nullable=True)
    created_at = db.Column(db.String())
    epoch_created_at = db.Column(db.Integer())

    def __init__(self, **kwargs):
        super(EmailLog, self).__init__(**kwargs)

        self.created_at = datetime.datetime.utcnow().isoformat()
        self.epoch_created_at = int(time.time())

    @staticmethod
    def log_to_db(**kwargs):
        log = EmailLog(**kwargs)
        db.session.add(log)
        try:
            db.session.commit()
        except Exception as e:
            print("failed to log to db:{}".format(str(e)))
            db.session.rollback()
