import datetime
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue

from rodenia_api.app import create_app
from rodenia_api.clock_helpers.oldest_job_report import oldest_job_alert
from rodenia_api.clock_helpers.queues_config import (
    NAMESPACE_ALERT_FREQUENCY_IN_MINS, OLDEST_JOB_ON_QUEUE
)
from rodenia_api.extensions import redis_conn

app = create_app()

logging.basicConfig()
rt_queue = Queue('real_time', connection=redis_conn)
default_queue = Queue('default', connection=redis_conn)
alert_queue = Queue('alert', connection=redis_conn)
sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=NAMESPACE_ALERT_FREQUENCY_IN_MINS[OLDEST_JOB_ON_QUEUE],
                     next_run_time=datetime.datetime.now())
def oldest_job_on_queues_alert_job():
    alert_queue.enqueue_call(oldest_job_alert, timeout=600)
    print("enqueued oldest job alert job")


sched.start()
