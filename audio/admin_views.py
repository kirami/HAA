from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.core.mail import send_mail

from audio.forms import ContactForm, BidSubmitForm

from audio.models import Address, Item, Bid

from datetime import datetime  

import logging
import json



# Get an instance of a logger
logger = logging.getLogger(__name__)

def test(request):
	return render_to_response('endAuction.html', {"form":""}, context_instance=RequestContext(request))

def endAuction(request):
	#TODO only super admins can do this
	return HttpResponse({"test":"success"}, content_type="application/json")