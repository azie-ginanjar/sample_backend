import datetime

from rodenia_api.extensions import db


class AlertLog(db.Model):
    __tablename__ = 'alert_log'
    id = db.Column(db.Integer(), primary_key=True)
    message = db.Column(db.String())
    namespace = db.Column(db.String())
    slack_code_status = db.Column(db.Integer())
    slack_response = db.Column(db.String())
    created_at = db.Column(db.String())

    def __init__(self, message, namespace, slack_code_status, slack_response, created_at=None):
        self.message = message
        self.namespace = namespace
        self.slack_code_status = slack_code_status
        self.slack_response = slack_response

        if not created_at:
            self.created_at = datetime.datetime.utcnow().isoformat()
        else:
            self.created_at = created_at

    @staticmethod
    def log_to_db(message, namespace, slack_code_status, slack_response):
        log = AlertLog(message, namespace, slack_code_status, slack_response)
        db.session.add(log)
        try:
            db.session.commit()
        except Exception as e:
            print("failed to log to db:{}".format(str(e)))
            db.session.rollback()
