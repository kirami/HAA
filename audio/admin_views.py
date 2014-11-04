from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.core.mail import send_mail

from audio.forms import ContactForm, BidSubmitForm, BulkConsignment

from audio.models import Address, Item, Bid, Invoice, Payment, Auction, Consignor
from audio.utils import *
from audio.mail import *

from datetime import datetime  

import json

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def test(request):
	return "test"


def sendAllConsignorReports(request):
	auctionId = d.get("auctionId")
	template = d.get("template")
	return consignorReport(auctionId, template)

def sendTemplateEmail(request):
	d = request.POST
	consignorId = d.get("consignorId")
	auctionId = d.get("auctionId")
	template = d.get("template")
	return consignorReportById(request, consignorId, auctionId, template)

def consignorReportById(request, consignorId, auctionId, template = None):
	data = getAllConsignmentInfo(consignorId, auctionId)	
	getHeaderData(data, auctionId)
	
	if template:
		msg = getEmailMessage("fosterthefelines@gmail.com","test",{"data":data}, template)
		sendEmail(msg)
		return HttpResponse(json.dumps({"success":True}), content_type="application/json")
		

	return render_to_response('admin/audio/consignorReportById.html', {"data":data}, context_instance=RequestContext(request))


def consignorReport(request, auctionId, template = None):
	data = {}
	#all consignors, consignor total money
	data["total"] = getSumWinners(auctionId)
	getHeaderData(data, auctionId)
	messages = {}
	
	consignors = getConsignmentWinners(auctionId = auctionId)
	for consignor in consignors:
		consignorId = consignor["consignor_id"]
		consignor = Consignor.objects.get(id = consignorId)
		consignInfo = consignorId
		indData = getAllConsignmentInfo(consignorId, auctionId)
		data[consignInfo] = indData

		if template:
			msg = getEmailMessage("fosterthefelines@gmail.com","test",{"data":indData}, template)
			messages.append(msg)

	if template:
		sendBulkEmail(messages)
		return HttpResponse(json.dumps({"success":True}), content_type="application/json")

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

	data["totalPayments"] = getTotalPaymentAmount()
	data["totalInvoices"] = getTotalInvoiceAmount()
	data["remaining"] = data["totalPayments"] - data["totalInvoices"]

	#per user
	data["unbalancedUsers"] = getUnbalancedUsers()
	return render_to_response('admin/audio/balances.html', {"data":data}, context_instance=RequestContext(request))	

def reportByUser(request):
	data = {}
	auctionId = 1
	data["winningBids"] = getWinningBids(auctionId, userId = 1)
	return render_to_response('admin/audio/winners.html', {"data":data}, context_instance=RequestContext(request))	


def markWinners(request, auctionId):
	#TODO - is this after invoice run?  are you sure?
	#set all winners for this auction to 0
	data = {}
	data["success"] = False
	if request.method == "POST":

		resetWinners(auctionId)

		dupes = getDuplicateItems(auctionId)
		bids = getOrderedBids(auctionId)
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
	 	data["success"]=True

	data["auctions"] = Auction.objects.filter(locked = False)

	return render_to_response('admin/audio/markWinners.html', {"data":data}, context_instance=RequestContext(request))



def winners(request, auctionId):
	data = {}
	winners = getAlphaWinners(auctionId)
	for winner in winners:
		try:
			#logger.error("winner: " + winner)
			address = Address.objects.get(user_id = winner["id"])
			winner["zipcode"] = address.zipcode
		except:
			pass
	
	data["winningBids"] = winners
	getHeaderData(data, auctionId)
	
	return render_to_response('admin/audio/winners.html', {"data":data}, context_instance=RequestContext(request))

def losers(request, auctionId):
	data = {}
	getHeaderData(data, auctionId)
	return render_to_response('admin/audio/losers.html', {"data":data}, context_instance=RequestContext(request))

def wonItems(request, auctionId):
	data = {}
 	getHeaderData(data, auctionId)
	return render_to_response('admin/audio/wonItems.html', {"data":data}, context_instance=RequestContext(request))

def unsoldItems(request, auctionId):
	data = {}
	getHeaderData(data, auctionId)
	return render_to_response('admin/audio/unsoldItems.html', {"data":data}, context_instance=RequestContext(request))

def bulkConsignment(request, auctionId):
	
	if request.method == 'POST':
		form = BulkConsignment(request.POST)
		if form.is_valid():			
			new_user = form.save()
			return HttpResponseRedirect("/admin/audio/consignment/")
		else:
			return render_to_response('admin/audio/bulkConsignment.html', {"form":form}, context_instance=RequestContext(request))

	else:
		form = BulkConsignment(auctionId = auctionId)

	return render_to_response('admin/audio/bulkConsignment.html', {"form":form}, context_instance=RequestContext(request))


def runReport(request, auctionId):
 	data = {}
 	getHeaderData(data, auctionId)

	return render_to_response('admin/audio/report.html', {"data":data}, context_instance=RequestContext(request))

#view for marking entire bidder paid, not just per item