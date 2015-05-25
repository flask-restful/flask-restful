# _*_ coding: utf-8 _*_

__author__ = 'radik'

import traceback

from flask import request as __request
from flask import current_app
from flask_mail import Message as __Message



# create a closure to track the sender and recipients
def email_exception(mail, exception):
    try:
        current_app.config['DEFAULT_MAIL_SENDER']
        current_app.config['ADMINISTRATORS']
    except KeyError:
        return

    msg = __Message("[Flask|ErrorMail] Exception Detected: %s" % exception.message,
                    sender=current_app.config['DEFAULT_MAIL_SENDER'],
                    recipients=current_app.config['ADMINISTRATORS'])
    msg_contents = [
        'Traceback:',
        '='*80,
        traceback.format_exc(),
    ]
    msg_contents.append('\n')
    msg_contents.append('Request Information:')
    msg_contents.append('='*80)
    environ = __request.environ
    environkeys = sorted(environ.keys())
    for key in environkeys:
        msg_contents.append('%s: %s' % (key, environ.get(key)))

    msg.body = '\n'.join(msg_contents) + '\n'
    try:
        mail.send(msg)
    except:
         current_app.logger.exception("Error send email")
