from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def sendEmail(to, subject, data):
	plaintext = get_template('email/email.txt')
	htmly     = get_template('email/email.html')

	d = Context(data)
	#d = Context({ 'username': "testUser" })

	subject, from_email, to = subject, 'kirajmd@gmail.com', to
	text_content = plaintext.render(d)
	html_content = htmly.render(d)
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
	msg.attach_alternative(html_content, "text/html")
	msg.send()