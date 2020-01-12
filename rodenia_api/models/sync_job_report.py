from rodenia_api.extensions import db


class SyncJobReport(db.Model):
    __tablename = 'sync_job_report'
    id = db.Column(db.Integer(), primary_key=True)
    seller_id = db.Column(db.String(), nullable=False)
    sync_type = db.Column(db.String())
    sync_status = db.Column(db.String())
    start_date_epoch = db.Column(db.Integer())
    end_date_epoch = db.Column(db.Integer())

    def __init__(self, **kwargs):
        super(SyncJobReport, self).__init__(**kwargs)
