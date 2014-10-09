from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.core.mail import send_mail

from audio.forms import ContactForm, BidSubmitForm

from audio.models import Address, Item, Bid
from audio.utils import getNoBidItems, getMaxBids, getWinners

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

def markWinners(request):
	#only if not already marked
	#get each bid per item
	#get max bid
	# tie?
	#select max(a.amount), i.id from audio_bid a, audio_item i where i.id = a.item_id group by id;

	maxBids = maxBids = getMaxBids()
 	for bid in maxBids:
 		bid.winner = True
 		bid.save()
	


	return HttpResponse({"test":"success"}, content_type="application/json")

def runReport(request):
 	''' get all items with bids, 
 		get winners
 		mark winning bids
 		print on screen
 		option to print invoices
 		option to email invoices
 		users with no winning bids 
 		items with no bids  --  mysql> select * from audio_item where id not in (select item_id from audio_bid);

 	'''
 	winners = getWinners()

	return render_to_response('report.html', {"x":winners}, context_instance=RequestContext(request))

#view for marking entire bidder paid, not just per item