import requests
import json

from rodenia_api.models import AlertLog


def send_to_slack(url, data):
    return requests.post(url, data)


def alert_slack(messages, namespace):
    status_code = None
    response = None
    slack_message = None
    if len(messages) > 0:
        slack_message = {
            "text": "\n".join(messages)
        }
        res = send_to_slack("https://hooks.slack.com/services/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",
                            json.dumps(slack_message))

        status_code = res.status_code
        response = res.text

    AlertLog.log_to_db(str(slack_message), namespace, status_code, response)
