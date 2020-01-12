import datetime
from rq import Queue
from rodenia_api.extensions import redis_conn
from rodenia_api.clock_helpers.queues_config import QUEUES, OLDEST_JOB_ON_QUEUE
from rodenia_api.clock_helpers import alert_util


def oldest_job_alert():
    messages = []
    for queue, sla in QUEUES.iteritems():
        print(queue, sla)
        q = Queue(queue, connection=redis_conn)
        queued_job_ids = q.job_ids
        if len(queued_job_ids) > 0:
            first_job = queued_job_ids[0]
            job = q.fetch_job(first_job)
            threshold = (datetime.datetime.utcnow()-datetime.timedelta(minutes=sla)).isoformat()
            # created_at is when a job is created before adding to the queue
            created_at = job.created_at.isoformat()
            enqueued_at = job.enqueued_at.isoformat()
            if created_at >= threshold:
                continue

            messages.append(
                "{} function from {} queue doesn't meet SLA requirement of {} minutes. Created at {}, Enqueued at {}".format(
                    job.func_name, queue, sla, created_at, enqueued_at
                )
            )

    alert_util.alert_slack(messages, OLDEST_JOB_ON_QUEUE)
