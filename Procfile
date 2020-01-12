web: newrelic-admin run-program gunicorn rodenia_api.wsgi:app
clock_scheduler: python rodenia_api/clock.py
worker: python rodenia_api/worker.py default high low
rt_worker: python rodenia_api/worker.py real_time
alert_worker: python rodenia_api/worker.py alert
backfill_worker: python rodenia_api/worker.py backfill
user_jobs_worker: python rodenia_api/worker.py user_facing_jobs