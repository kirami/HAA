from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.core import mail
from django.contrib.sites.models import Site

from django.conf import settings

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def sendEmail(msg):
	try:
		if not settings.ALLOW_EMAIL:
			logger.info("sending email is set to disallow")
			return
		msg.send()
	except Exception as e:
		logger.error("send email error: %s" % e)


def sendBulkEmail(messages, emailType=None):
	try:
		logger.info("Sending %s emails of type: %s" % (len(messages), emailType))
		if not settings.ALLOW_EMAIL:
			logger.info("sending email is set to disallow")
			return

		connection = mail.get_connection()   # Use default email connection
		connection.send_messages(messages)
	except Exception as e:
		logger.error("send bulk email error: %s" % e)

def getEmailMessage(to, subject, data, template, record = False):
	plaintext = get_template('email/'+template+'.txt')
	htmly     = get_template('email/'+template+'.html')
	#domain = Site.objects.get_current().domain
	#TODO get from setting or something else 
	data["domain"] = settings.EMAIL_URL
	d = Context(data)
	#TODO get email from settings
	subject, from_email, to = subject, settings.DEFAULT_FROM_EMAIL, to
	text_content = plaintext.render(d)
	html_content = htmly.render(d)
	msg = EmailMultiAlternatives(subject, text_content, "Hawthorn's Antique Audio <"+from_email+">", [to])
	msg.attach_alternative(html_content, "text/html")

	if record:
		pdf = open('/srv/hawthorn/files/RosevilleRecord.pdf', 'rb')
		msg.attach('RosevilleRecord.pdf', pdf.read(),'application/pdf')

	
	return msg
