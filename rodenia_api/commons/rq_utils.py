import backoff

from rodenia_api.extensions import redis_conn
from rq import Connection, get_failed_queue, Queue
from rq.job import Job
from rodenia_api.models import User
import traceback


def get_failed_jobs_by_index(field_to_index_by="seller_id"):
    failed_job_data_by_index = {}
    with Connection(redis_conn):
        fq = get_failed_queue()
        for job in fq.jobs:
            print(job)
            try:
                for arg in job.args:
                    if type(arg) != User:
                        continue

                    data = {
                        "exc_info": job.exc_info,
                        "started_at": job.started_at.isoformat(),
                        "ended_at": job.ended_at.isoformat(),
                        "func_name": job.func_name
                    }

                    if field_to_index_by == "seller_id":
                        index = arg.seller_id
                    elif field_to_index_by == "username":
                        index = arg.username
                    else:
                        raise Exception("Invalid field_to_index_by value: {}".format(field_to_index_by))

                    if index not in failed_job_data_by_index:
                        failed_job_data_by_index[index] = [data]
                    else:
                        failed_job_data_by_index[index].append(data)
            except Exception as e:
                print(
                    "While getting failed jobs by index, we failed to iterate over rq job args: {}".format(
                        traceback.format_exc()
                    )
                )

    return failed_job_data_by_index


@backoff.on_exception(backoff.fibo, Exception, max_tries=3)
def fetch_job(queue, job_id):
    return queue.fetch_job(job_id)
