from rq import Worker, Queue, Connection
from extensions import redis_conn
from rodenia_api.app import create_app
import sys
from raven import Client
from raven.transport.http import HTTPTransport
from rq.contrib.sentry import register_sentry

app = create_app()
client = Client(app.config.get('SENTRY_DSN'), transport=HTTPTransport)

listen = ['default']
if len(sys.argv) > 1:
    listen = [queue_name.strip() for queue_name in sys.argv[1:]]

if __name__ == '__main__':
    with Connection(redis_conn):
        with app.app_context():
            worker = Worker(map(Queue, listen))
            register_sentry(client, worker)
            worker.work()
