from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.core.mail import send_mail

from audio.forms import ContactForm, BidSubmitForm, BulkConsignment, AdminBidForm

from audio.models import Address, Item, Bid, Invoice, Payment, Auction, Consignor, UserProfile
from audio.utils import *
from audio.mail import *

from datetime import datetime  

import json

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def test(request):
	return "test"


def createBid(request, auctionId):
	data = {}
	
	if request.method == "POST":
		form = AdminBidForm(auctionId, request.POST)
		if form.is_valid():
			form.save(auctionId = auctionId)
			data["form"] = form
			return render_to_response('admin/audio/createBid.html', {"data":data, "success": True}, context_instance=RequestContext(request))
		

	data["form"] = AdminBidForm(auctionId = 2)
	data["auction"] = auctionId
	return render_to_response('admin/audio/createBid.html', {"data":data}, context_instance=RequestContext(request))


def endBlindAuction(request, auctionId):
	invoices = {}
	logger.error( "here")
	#make sure to do all manual stuff first
	auction = Auction.objects.get(id = auctionId)
	now = datetime.now()
	
	if auction.blind_locked == True:
		return HttpResponse(json.dumps({"success":False, "msg":"This auction is locked"}), content_type="application/json")

	if now < auction.end_date:
		return HttpResponse(json.dumps({"success":False, "msg":"The blind auction time isn't up."}), content_type="application/json")

	#mark winners
	markWinners(auction.id)
	
	#get all won items before end date
	winners = getWinningBids(auctionId, date = auction.end_date)
	#figure sums & shipping

	for winner in winners:
		userId = winner.user_id

		if userId not in invoices:
			logger.error( "user not in invoices")
			user = User.objects.get(id = userId)
			sum = getWinnerSum(auctionId, userId, date = auction.end_date)
			invoicedAmount = sum["sum"]
			#TODO shipping amount
			invoice = Invoice.objects.create(user = user, auction = auction, invoiced_amount = invoicedAmount, invoice_date = datetime.now())
			invoices[userId] = invoice.id
			winner.invoice = invoice
			winner.save()
		else:
			invoice = Invoice.objects.get(id = invoices[userId])
			winner.invoice = invoice	
			winner.save()

	auction.blind_locked = True
	auction.save()


	return HttpResponse(json.dumps({"success":True}), content_type="application/json")


def endFlatAuction(request, auctionId, userId = None):
	now = datetime.now()
	#for all bids in auction not invoiced

	#make sure to do all manual stuff first
	auction = Auction.objects.get(id = auctionId)
	if auction.flat_locked == True and userId == None:
		return HttpResponse(json.dumps({"success":False, "msg":"This auction is flat locked"}), content_type="application/json")

	if now < auction.second_chance_end_date:
		return HttpResponse(json.dumps({"success":False, "msg":"The flat auction time isn't up."}), content_type="application/json")


	#DO NOT mark winners - they should already be marked

	#get all won items before end date
	if userId == None:
		winners = getWinningBids(auctionId, onlyNonInvoiced = True)
		#TODO lock 2nd auction
	else:
		winners = getWinningBids(auctionId, userId = userId, onlyNonInvoiced = True)
	#figure sums & shipping

	for winner in winners:
		userId = winner.user_id

		#if no invoice from blind auction, create
		if winner.invoice == None:
			user = User.objects.get(id = userId)
			sum = getWinnerSum(auctionId, userId, onlyNonInvoiced = True)
			invoicedAmount = sum["sum"]
			#TODO shipping amount
			invoice = Invoice.objects.create(user = user, auction = auction, invoiced_amount = 0, second_chance_invoice_amount = invoicedAmount, second_chance_invoice_date = now, )
			winner.invoice = invoice
			winner.save()
		else:
			invoice = winner.invoice
			
			if invoice.second_chance_invoice_amount == None:
				sum = getWinnerSum(auctionId, userId, onlyNonInvoiced = True)
				invoicedAmount = sum["sum"]
				invoice.second_chance_invoice_amount = invoicedAmount
				#shipping
				invoice.second_chance_invoice_date = datetime.now()
				invoice.save()
	if userId == None:			
		auction.flat_locked = True
		auction.save()
	return HttpResponse(json.dumps({"success":True}), content_type="application/json")

def userBreakdown(request):
	data = {}
	return render_to_response('admin/audio/userBreakdown.html', {"data":data}, context_instance=RequestContext(request))

def endAuction(request, auctionId):
	data = {}
	data["auctionId"]=auctionId

	auction = Auction.objects.get(id=auctionId)
	if auction.flat_locked:
		data["flat_locked"] = True
	if auction.blind_locked:
		data["blind_locked"] = True


	return render_to_response('admin/audio/endAuction.html', {"data":data}, context_instance=RequestContext(request))


def invoices(request, auctionId):
	data = {}
	data["auctionId"]=auctionId
	return render_to_response('admin/audio/invoiceAdmin.html', {"data":data}, context_instance=RequestContext(request))


def sendLoserLetters(request, auctionId):
	losers = getLosers(auctionId)
	messages = []
	template = "loserLetter"
	data = {}
	data["auctionId"] = auctionId

	for loser in losers:
		profile = UserProfile.objects.get(user_id = loser.user_id)
		user = User.objects.get(id = loser.user_id )
		#todo if profile has send emails
		if profile and profile.email_invoice:
			msg = getEmailMessage(user.email,"test",{"data":data}, template)
			messages.append(msg)

	if template :
		sendBulkEmail(messages)
		return HttpResponse(json.dumps({"success":True}), content_type="application/json")

	
	return HttpResponse(json.dumps({"success":True}), content_type="application/json")


def getInvoices(request, auctionId, userId = None, template=None):
	data = {}
	if userId != None:
		data["invoice"]=getSumWinners(auctionId, userId)
	return render_to_response('admin/audio/invoice.html', {"data":data}, context_instance=RequestContext(request))


def sendInvoices(request, auctionId):
	
	auction = Auction.objects.get(id = auctionId)
	
	winners = getAlphaWinners(auctionId)
	messages = []
	template = "invoice"
	data = {}

	for winner in winners:
		profile = UserProfile.objects.get(user_id = winner["id"])
		if profile and profile.email_invoice:
			user = User.objects.get(id = winner["id"] )
			data["invoice"] = getSumWinners(auctionId, winner["id"])
			msg = getEmailMessage(user.email,"test",{"data":data}, template)
			messages.append(msg)
			
	if template :
		sendBulkEmail(messages)
		return HttpResponse(json.dumps({"success":True}), content_type="application/json")

	
	return HttpResponse(json.dumps({"success":True}), content_type="application/json")
		



def sendAllConsignorReports(request):
	d = request.POST
	auctionId = d.get("auctionId")
	logger.error("auction:")
	logger.error(auctionId)
	template = "singleConsignorReport"
	return consignorReport(request, auctionId, template)

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
	messages = []
	
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


def markWinners(auctionId):
	#TODO - is this after invoice run?  are you sure?
	#set all winners for this auction to 0
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
 	
	return True


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