from rodenia_api.extensions import db
from rodenia_api.models import SyncJobReport
import time


def record_sync_status(seller_id, sync_type, status, start_time):
    end_time = time.time()
    report = SyncJobReport(
        seller_id=seller_id,
        sync_type=sync_type,
        sync_status=status,
        start_date_epoch=start_time,
        end_date_epoch=end_time
    )

    db.session.add(report)

    try:
        db.session.commit()
    except Exception as e:
        print(e.args)
        db.session.rollback()
