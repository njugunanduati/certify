from threading import Thread
from flask import render_template
from flask_mail import Message
from app import app, mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = user.get_token()
    username = '{} {}'.format(user.first_name, user.last_name)
    send_email('[Certify App] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('emails/reset_password.txt',
                                         user=username, token=token),
               html_body=render_template('emails/reset_password.html',
                                         user=username, token=token))
    

def send_confirm_email(user):
    token = user.get_token()
    username = '{} {}'.format(user.first_name, user.last_name)
    send_email('[Certify App] Confirm Email',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('emails/confirm_email.txt',
                                         user=username, token=token),
               html_body=render_template('emails/confirm_email.html',
                                         user=username, token=token))