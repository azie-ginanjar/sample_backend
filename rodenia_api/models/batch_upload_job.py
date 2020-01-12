from rodenia_api.extensions import db
import datetime

"""
This model is designed to support the use case of a batch upload,
where there needs to be a parent batch upload ID associated with
each individual upload job.
"""


class BatchUploadJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer())
    generated_report_id = db.Column(db.Integer())
    job_status = db.Column(db.String())
    error_message = db.Column(db.String())
    created_at = db.Column(db.String())
    updated_at = db.Column(db.String())

    def __init__(self, user_id, job_status, error_message=None, generated_report_id=None):
        self.user_id = user_id
        self.generated_report_id = generated_report_id
        self.created_at = datetime.datetime.utcnow().isoformat()
        self.updated_at = datetime.datetime.utcnow().isoformat()
