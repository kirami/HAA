from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.core.mail import send_mail

from audio.forms import ContactForm, BidSubmitForm

from audio.models import Address, Item, Bid
from audio.utils import getNoBidItems, getMaxBids, getWinners, getLosers, getWinBidsByUser
from audio.utils import getBidItems, getDuplicateItems, getAlphaWinners, getSumWinners

from datetime import datetime  

import logging
import json



# Get an instance of a logger
logger = logging.getLogger(__name__)

def test(request):
	return render_to_response('endAuction.html', {"form":""}, context_instance=RequestContext(request))

def reportByUser(request):
	data = {}
	data["winningBids"] = getWinBidsByUser(1)
	return render_to_response('winners.html', {"data":data}, context_instance=RequestContext(request))	

def endAuction(request):
	#TODO only super admins can do this
	return HttpResponse({"test":"success"}, content_type="application/json")

def markWinners(request):
	#get all dups, do those first:

	dupes = getDuplicateItems()

	for dupe in dupes:
		dupeBids = getTopDupeBids(dupe.id, dupe.quantity)
		for dupeBid in dupeBids:
 			dupeBid.winner = True
 			dupeBid.save()

	maxBids = maxBids = getMaxBids()
 	for bid in maxBids:
 		if bid.winner != True:
 			bid.winner = True
 			bid.save()

	return HttpResponse({"test":"success"}, content_type="application/json")


def winners(request):
	data = {}
	data["winningBids"] = getAlphaWinners()
	return render_to_response('winners.html', {"data":data}, context_instance=RequestContext(request))

def losers(request):
	data = {}
	data["losingBids"] = getLosers()
	return render_to_response('losers.html', {"data":data}, context_instance=RequestContext(request))

def wonItems(request):
	data = {}
	data["soldItems"] = getWinners()
	return render_to_response('wonItems.html', {"data":data}, context_instance=RequestContext(request))

def unsoldItems(request):
	data = {}
	data["unsoldItems"] = getNoBidItems()
	return render_to_response('unsoldItems.html', {"data":data}, context_instance=RequestContext(request))

def runReport(request):
 	data = {}
 	''' get all items with bids, 
 		get winners
 		mark winning bids
 		print on screen
 		option to print invoices
 		option to email invoices
 		users with no winning bids 
 		items with no bids

 	'''
 	winners = getWinners()
 	maxBids = getMaxBids()
 	noBids = getNoBidItems()
 	losers = getLosers()

 	data["auctionId"] = 1
 	data["winners"] = winners
 	data["maxBids"] = maxBids
 	data["losers"] = losers
 	data["loserCount"] = len(losers)
 	data["wonItems"] = getBidItems()
 	data["noBidItems"] = len(noBids)
 	data["total"] = getSumWinners()

	return render_to_response('report.html', {"data":data}, context_instance=RequestContext(request))

#view for marking entire bidder paid, not just per item