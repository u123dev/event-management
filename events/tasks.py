from smtplib import SMTPException

from celery import shared_task

from django.core.mail import send_mail


@shared_task
def send_notification(subject, message, from_email, to_email):
    try:
        return send_mail(subject, message, from_email, [to_email, ])
    except SMTPException:
        pass
