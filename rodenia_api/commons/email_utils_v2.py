import os
import traceback

import sendgrid
from sendgrid.helpers.mail import *

API_KEY = os.environ.get("SENDGRID_API_KEY")
FROM_EMAIL = "Rodenia<ron.joshi@rodenia.com>"


def send_plain_email(to_email, subject, body, is_multiple, reply_to=None, is_html=False, html_content=None):
    sg = sendgrid.SendGridAPIClient(API_KEY)
    from_email = Email(FROM_EMAIL)

    to_emails = to_email
    if not isinstance(to_email, str):
        to_emails = (to_emails, )
        for email in to_email:
            to_emails += (email, )

    plain_content = Content("text/plain", body)

    if not is_html:

        mail = Mail(
            from_email=from_email,
            subject=subject,
            plain_text_content=plain_content,
            is_multiple=is_multiple,
            to_emails=to_emails
        )
    else:
        content = Content("text/html", html_content)

        mail = Mail(
            from_email=from_email,
            subject=subject,
            plain_text_content=plain_content,
            html_content=content,
            is_multiple=is_multiple,
            to_emails=to_emails
        )

    if reply_to:
        mail.reply_to = reply_to

    response = sg.client.mail.send.post(request_body=mail.get())
    return {
        "error": None,
        "status_code": response.status_code,
        "body": response.body,
        "headers": response.headers
    }


def send_transactional_dynamic_template_email(to_email, template_id, dynamic_template_data, email_from, email_reply_to):
    sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
    personalization = Personalization()
    personalization.add_to(Email(to_email))
    mail = Mail()
    mail.from_email = Email(FROM_EMAIL, email_from)
    mail.subject = "I'm replacing the subject tag"
    mail.add_personalization(personalization)
    mail.template_id = template_id
    mail.reply_to = Email(email_reply_to)
    personalization.dynamic_template_data = dynamic_template_data
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
        return {
            "error": None,
            "status_code": response.status_code,
            "body": response.body,
            "headers": response.headers
        }
    except Exception as e:
        print(str(e))
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }


def send_coupon_email(to_email, email_subject, email_headline, email_body, button_url, email_from, email_reply_to):
    template_id = "d-7052952b5ca14fa5857f483fea3d546a"
    dynamic_template_data = {
        'email_subject': email_subject,
        'email_headline': email_headline,
        'email_body': email_body,
        'button_url': button_url
    }
    return send_transactional_dynamic_template_email(to_email, template_id, dynamic_template_data, email_from,
                                                     email_reply_to)


def send_followup_email(to_email, email_subject, email_headline, email_body, email_from, email_reply_to):
    template_id = "d-a854990c25a74b54909bb3a45e1d8808"
    dynamic_template_data = {
        'email_subject': email_subject,
        'email_headline': email_headline,
        'email_body': email_body
    }
    return send_transactional_dynamic_template_email(to_email, template_id, dynamic_template_data, email_from,
                                                     email_reply_to)


def send_waitlist_email(to_email, email_subject, email_headline, email_body, email_from, email_reply_to):
    template_id = "d-a854990c25a74b54909bb3a45e1d8808"
    dynamic_template_data = {
        'email_subject': email_subject,
        'email_headline': email_headline,
        'email_body': email_body
    }
    return send_transactional_dynamic_template_email(to_email, template_id, dynamic_template_data, email_from,
                                                     email_reply_to)
