QUEUES = {
    'real_time': 5,
    'low': 60,
    'normal': 60,
    'high': 10,
    'user_facing_jobs': 10,
    'backfill': 120,
    'default': 60,
    # 'failed': 10
}

ALERT_STALENESS = 'ALERT_STALENESS'
OLDEST_JOB_ON_QUEUE = 'OLDEST_JOB_ON_QUEUE'

NAMESPACE_ALERT_FREQUENCY_IN_MINS = {
    OLDEST_JOB_ON_QUEUE: 10
}

STALENESS_LIMIT_IN_PERCENTAGE = {
}
