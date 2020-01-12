from datetime import datetime
import decimal
import json
import os
import re

import boto
import dateparser
from boto.s3.key import Key
from mailchimp3 import MailChimp
from sqlalchemy import func

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
REGION_HOST = os.environ.get("REGION_HOST")
MAILCHIMP_API_KEY = os.environ.get("MAILCHIMP_API_KEY")


def download_file_from_s3(bucket_name, filename):
    try:

        conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                               AWS_SECRET_ACCESS_KEY)

        print ('Downloading {} from Amazon S3 bucket {}'.format(filename, bucket_name))

        bucket = conn.get_bucket(bucket_name)
        k = Key(bucket)
        k.key = filename
        file = k.get_contents_as_string()
        return file
    except Exception as e:
        print("S3 file download didn't work")
        print(e)
        return None


def save_file_in_s3(bucket_name, filename):
    try:
        conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                               AWS_SECRET_ACCESS_KEY)

        # print 'Uploading %s to Amazon S3 bucket %s'.format(filename, bucket_name)

        bucket = conn.get_bucket(bucket_name)
        k = Key(bucket)
        k.key = filename
        k.set_contents_from_filename("uploads/" + filename)
        print('Upload to S3 succeeded.')
        return True
    except Exception as e:
        print("S3 file upload didn't work")
        print(e)
        return False


def save_file_in_s3_by_file(bucket_name, file, filename):
    try:
        conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                               AWS_SECRET_ACCESS_KEY, host=REGION_HOST)

        # print 'Uploading %s to Amazon S3 bucket %s'.format(filename, bucket_name)

        bucket = conn.get_bucket(bucket_name)
        k = Key(bucket)
        k.key = filename
        k.set_contents_from_file(file)
        print('Upload to S3 succeeded.')
        return True
    except Exception as e:
        print("S3 file upload didn't work")
        print(e)
        return False


def safe_dateparse(date):
    try:
        return dateparser.parse(date)
    except Exception as e:
        return None


def safe_datestr(date):
    try:
        if type(date) == str or type(date) == unicode:
            date = dateparser.parse(date)
        return datetime.datetime.strftime(date, "%Y-%m-%d")
    except Exception as e:
        print(e)
        return ""


def is_int(val):
    try:
        int(val)
        return True
    except Exception as e:
        return False


def safe_int(string):
    try:
        return int(string)
    except Exception as e:
        return 0


def is_float(string):
    try:
        float(string)
        return True
    except Exception:
        return False


def safe_float(string):
    try:
        return float(string)
    except Exception as e:
        return 0.0


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in allowed_extensions


def parse_error_report(errorString):
    cleaned_items_with_errors = []
    items_with_errors = re.findall(r'\(([^]]*)\)', errorString)
    for item in items_with_errors:
        item = item.replace('(', '').replace(')', '')
        properties = item.split(', ')
        item = {}
        for prop in properties:
            propertyName, propertyVal = prop.split('=')
            item[propertyName] = propertyVal
        cleaned_items_with_errors.append(item)

    return cleaned_items_with_errors


def alchemyencoder(obj):
    import decimal
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)


def clean_timestr(timestr):
    # zero-pad the timestr, in-case frontend passes back 8:30 instead of 08:30
    hour, minute = timestr.split(":")
    if len(hour) == 1:
        hour = '0' + hour
    if len(minute) == 1:
        minute = '0' + minute
    timestr = hour + ":" + minute
    return timestr


def float_or_none(string):
    try:
        return float(string)
    except Exception as e:
        return None


def int_or_none(string):
    try:
        return int(string)
    except Exception as e:
        return None


def get_isoformatted_date_from_arbitrary_date_input(date_input):
    try:
        return dateparser.parse(date_input).isoformat()
    except Exception as e:
        return None


def count_query_rows(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count


def get_service_endpoint():
    return {
        "sg": "https://api.lazada.sg/rest",
        "my": "https://api.lazada.com.my/rest",
        "th": "https://api.lazada.co.th/rest",
        "vn": "https://api.lazada.vn/rest",
        "ph": "https://api.lazada.com.ph/rest",
        "id": "https://api.lazada.co.id/rest"
    }


def generate_epoch_from_string_datetime(string_datetime, date_format='%Y-%m-%dT%H:%M:%S'):
    epoch = datetime(1970, 1, 1)
    return int((datetime.strptime(string_datetime, date_format) - epoch).total_seconds())


def subscribe_list_member(list_id, email):
    client = MailChimp(mc_api=MAILCHIMP_API_KEY)

    data = {
        'email_address': email,
        'status': 'subscribed'
    }

    response = client.lists.members.create(list_id, data)

    return response


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)
