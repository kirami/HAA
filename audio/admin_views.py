from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.core.mail import send_mail

from audio.forms import ContactForm, BidSubmitForm

from audio.models import Address, Item, Bid, Invoice, Payment
from audio.utils import *

from datetime import datetime  

import logging
import json



# Get an instance of a logger
logger = logging.getLogger(__name__)

def test(request):
	return render_to_response('endAuction.html', {"form":""}, context_instance=RequestContext(request))


def consignorReportById(request, consignorId):
	data = {}
	#get all consigned won items with 
	#get all consigned lost items
	#description / bidder/ win amount/ consign amount / haa amount


	notWon = getConsignedLosersById(consignorId)
	consignedItems = getConsignmentWinnersById(consignorId)
	
	consignTotal = 0
	haaTotal = 0
	total = 0
	for item in consignedItems:
		total += item["amount"]
		amount = item["amount"] * (item["percentage"] / 100)
		item["consignedAmount"] = amount
		consignTotal += amount
		item["HAA_amount"] = item["amount"] - amount
		haaTotal += item["HAA_amount"]

	data["consignedItems"] = consignedItems
	data["haaTotal"] = haaTotal
	data["consignorTotal"] = consignTotal
	data["total"] = total
	#data["consignorInfo"] = 
	data["unsoldItems"] = notWon

	return render_to_response('consignorReportById.html', {"data":data}, context_instance=RequestContext(request))


def consignorReport(request):
	data = {}
	#Gross auction total
	data["total"] = getSumWinners()
	consignedItems = getConsignmentWinners()
	consignTotal = 0
	haaTotal = 0
	for item in consignedItems:
		amount = item["amount"] * (item["percentage"] / 100)
		item["consignedAmount"] = amount
		#get correct HAA consignor id
		if item["consignor_id"] == 1:
			item["HAA"] = True
			haaTotal+=amount
		else: 
			consignTotal+=amount


	data["totalHAA"] =  haaTotal
	#consignorBidSums = getConsignorBidSums
	data["consignorBidSums"] =	1
	data["consignedTotal"] = consignTotal		
	data["consignedItems"] = consignedItems

	#if data["total"] != haaTotal + consignTotal:
	#	logger.error("Total for this auction consignment is not right.")

	#Name / Gross / Commission % / Amount due
	
	return render_to_response('consignorReport.html', {"data":data}, context_instance=RequestContext(request))	



def userBalanceInfo(request, userId):
	data = {}

	invoices = getInvoiceInfoByUser(userId)
	data["invoices"] = invoices
	data["payments"] = getPaymentInfoByUser(userId)
	data["remaining"] = invoices["sum"] - data["payments"]["sum"]
	data["user"] = User.objects.get(id=userId)
	return render_to_response('userBalance.html', {"data":data}, context_instance=RequestContext(request))	


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
	return render_to_response('balances.html', {"data":data}, context_instance=RequestContext(request))	

def reportByUser(request):
	data = {}
	data["winningBids"] = getWinBidsByUser(1)
	return render_to_response('winners.html', {"data":data}, context_instance=RequestContext(request))	

def endAuction(request):
	#TODO only super admins can do this
	return HttpResponse({"test":"success"}, content_type="application/json")

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