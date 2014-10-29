from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.core.mail import send_mail

from audio.forms import ContactForm, BidSubmitForm, BulkConsignment

from audio.models import Address, Item, Bid, Invoice, Payment
from audio.utils import *

from datetime import datetime  

import logging
import json



# Get an instance of a logger
logger = logging.getLogger(__name__)

def test(request):
	return "test"

def consignorReportById(request, consignorId):
	data = getAllConsignmentInfo(consignorId)	
	return render_to_response('admin/audio/consignorReportById.html', {"data":data}, context_instance=RequestContext(request))


def consignorReport(request):
	data = {}
	#all consignors, consignor total money
	data["total"] = getSumWinners()
	
	consignors = getConsignorBidSums()
	for consignor in consignors:
		consignInfo = consignor["consignor_id"]
		data[consignInfo] = getAllConsignmentInfo(consignor["consignor_id"])
		data[consignInfo]["firstName"] = consignor["first_name"]
		data[consignInfo]["lastName"] = consignor["last_name"]
	#Name / Gross / Commission % / Amount due
	
	return render_to_response('admin/audio/consignorReport.html', {"data":data}, context_instance=RequestContext(request))	



def userBalanceInfo(request, userId):
	data = {}

	invoices = getInvoiceInfoByUser(userId)
	data["invoices"] = invoices
	data["payments"] = getPaymentInfoByUser(userId)
	data["remaining"] = invoices["sum"] - data["payments"]["sum"]
	data["user"] = User.objects.get(id=userId)
	return render_to_response('admin/audio/userBalance.html', {"data":data}, context_instance=RequestContext(request))	


def calculateBalances(request):
	data = {}
	
	#get invoices for this auction?  
	#get unpaid invoices?
	#invoices amount total - paid amount total?
	#

	data["totalPayments"] = getTotalPaymentAmountByAuction()
	data["totalInvoices"] = getTotalInvoiceAmountByAuction()
	data["remaining"] = data["totalPayments"] - data["totalInvoices"]

	#per user
	data["unbalancedUsers"] = getUnbalancedUsers()
	return render_to_response('admin/audio/balances.html', {"data":data}, context_instance=RequestContext(request))	

def reportByUser(request):
	data = {}
	data["winningBids"] = getWinBidsByUser(1)
	return render_to_response('admin/audio/winners.html', {"data":data}, context_instance=RequestContext(request))	



def markWinners(request):
	#TODO - is this after invoice run?  are you sure?

	#set all winners for this auction to 0
	resetWinners()

	dupes = getDuplicateItems()
	bids = getOrderedBids()
	currentItemId = 0
	index = 0
 	for bid in bids:
 		if currentItemId != bid.item_id:
 			#reset
 			item = Item.objects.filter(id = bid.item_id)
 			if len(item) > 0:
 				quantity = int(item[0].quantity)
 			else:
 				quantity = 0

 			currentItemId = bid.item_id
 			index = 0 			

 		if bid.winner != True and index < quantity:
 			bid.winner = True
 			bid.save()
 		
 		index = index + 1	

	return HttpResponse({"test":"success"}, content_type="application/json")


def winners(request):
	data = {}
	data["winningBids"] = getAlphaWinners()
	return render_to_response('admin/audio/winners.html', {"data":data}, context_instance=RequestContext(request))

def losers(request):
	data = {}
	data["losingBids"] = getLosers()
	return render_to_response('admin/audio/losers.html', {"data":data}, context_instance=RequestContext(request))

def wonItems(request):
	data = {}
	data["soldItems"] = getWinners()
	return render_to_response('admin/audio/wonItems.html', {"data":data}, context_instance=RequestContext(request))

def unsoldItems(request):
	data = {}
	data["unsoldItems"] = getNoBidItems()
	return render_to_response('admin/audio/unsoldItems.html', {"data":data}, context_instance=RequestContext(request))

def bulkConsignment(request):
	
	if request.method == 'POST':
		logger.error("in post")
		form = BulkConsignment(request.POST)
		logger.error("form made")
		if form.is_valid():
			logger.error("form is valid")
			new_user = form.save()
			return HttpResponseRedirect("/admin/audio/consignment/")
		else:
			'''
			for field in form.errors.keys():
				print "ValidationError: %s[%s] <- \"%s\" %s" % (type(form),field,form.data[field],form.errors[field].as_text() )  
			'''
			logger.error(form.errors)
			return render_to_response('admin/audio/bulkConsignment.html', {"form":form}, context_instance=RequestContext(request))

	else:
		form = BulkConsignment()

	return render_to_response('admin/audio/bulkConsignment.html', {"form":form}, context_instance=RequestContext(request))


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

	return render_to_response('admin/audio/report.html', {"data":data}, context_instance=RequestContext(request))

#view for marking entire bidder paid, not just per item