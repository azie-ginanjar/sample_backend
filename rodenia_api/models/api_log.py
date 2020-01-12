import datetime

from rodenia_api.extensions import db


class APILog(db.Model):
    __tablename__ = 'api_log'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    seller_id = db.Column(db.String())
    url = db.Column(db.String())
    request_json = db.Column(db.String())
    response_content = db.Column(db.String())
    status_code = db.Column(db.String())
    created_at = db.Column(db.String())

    def __init__(self, user_id, seller_id, url, request_json, response_content, status_code):
        self.user_id = user_id
        self.seller_id = seller_id
        self.url = url
        self.request_json = request_json
        self.response_content = response_content
        self.status_code = status_code
        self.created_at = datetime.datetime.utcnow().isoformat()

    @staticmethod
    def log_to_db(user_id, seller_id, url, request_json, response_content, status_code):
        log = APILog(user_id, seller_id, url, request_json, response_content, status_code)
        db.session.add(log)
        try:
            db.session.commit()
        except Exception as e:
            print("failed to log to db:{}".format(str(e)))
            db.session.rollback()
