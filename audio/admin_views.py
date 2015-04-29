from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.conf import settings
from django.core import serializers
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required


from django import forms
from decimal import Decimal
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.core.mail import send_mail

from audio.forms import ContactForm, BidSubmitForm, BulkConsignment, AdminBidForm, \
UserCreateForm, ItemForm, ItemPrePopulateForm, InvoiceForm

from audio.models import Address, Item, Bid, Invoice, Payment, Auction, Consignor, UserProfile, Category, Label, Condition
from audio.utils import *
from audio.mail import *

from audio.views import send_registration_confirmation

from datetime import datetime, date 
import json, math, string, random, collections, csv

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



@staff_member_required
def testEmail(request):
	#password = User.objects.make_random_password()
	#user.set_password(password)
	messages = []
	user = request.user

	emailData={}
	emailData["user"] = user
	#emailData["password"] = password	
	#emailData["url"] = "http://haa/audio/accounts/confirm/" + str(profile.confirmation_code) + "/" + user.username
	msg = getEmailMessage(user.email,"Welcome to Hawthorn's Antique Audio!",{"data":emailData}, "newSystem")
	messages.append(msg)
	#emailList.append(user.email)
	#sendBulkEmail(messages)
	#sendEmail(msg)

	try:

		sendEmail(msg)
	except Exception as e:
		logger.error(e)
		return HttpResponse(json.dumps({"success":True, "error":str(e)}), content_type="application/json")
	
	return HttpResponse(json.dumps({"success":True}), content_type="application/json")


@staff_member_required
def printRecordLabels(request, auctionId, startingIndex = None):

	data = {}
	data["auction"] = Auction.objects.get(pk = auctionId)
	if startingIndex:
		data["items"] = Item.objects.filter(auction = auctionId, lot_id__gte = startingIndex).order_by("lot_id")  
	else:
		data["items"] = Item.objects.filter(auction = auctionId).order_by("lot_id")  

	return render_to_response('admin/audio/printRecordLabels.html', {"data":data}, context_instance=RequestContext(request))


@staff_member_required
def conditionsCheck(request, auctionId):
	data = {}
	
	auction = None
	auctions = Auction.objects.filter(pk=auctionId)
	if len(auctions) < 1:
		data["badAuction"]=True
		logger.error("bad auction in conditions")
		return render_to_response('admin/audio/conditions.html', {"data":data}, context_instance=RequestContext(request))
	else:
		auction = auctions[0]
		data["auction"]=auction
		if auction.blind_locked:
			data["blindLocked"]=True

	conditions = Condition.objects.filter(auction = auctionId, done=False)
	if len(conditions) < 1:
		data["noConditions"] = True	

	if request.method == 'POST':
		
		data["success"] = markWinners(auctionId)
		
		
		info = []
		for condition in conditions:
			cond = {}
			cond["condition"] = condition
			cond["bids"] = getWinnerSum(auctionId=auctionId, userId = condition.user.id)
			info.append(cond)
			#logger.error("sum: %s" % sum)
	
		
		data["info"] = info	
		return render_to_response('admin/audio/conditionsReport.html', {"data":data}, context_instance=RequestContext(request))

	return render_to_response('admin/audio/conditions.html', {"data":data}, context_instance=RequestContext(request))


@staff_member_required
def winningBidReport(request, auctionId):
	logger.info("test")
	data = {}
	data["winningBids"] = getWinningBids(auctionId)
	#data["auction"]=Auction.objects.get(pk=auctionId)
	getHeaderData(data, auctionId)
	return render_to_response('admin/audio/winningBids.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def sendWinningBidReport(request):
	data = {}
	messages = []
	emailList = []
	noEmailList = []
	
	auctionId = request.POST.get("auctionId", None)
	userId = request.POST.get("userId", None)
	auction = None
	#TODO only winning bids or any bidder?
	winningBids = getWinningBids(auctionId)
	
	try:
		auction = Auction.objects.get(pk=auctionId)
		#if user is specified only send to that user
		if userId:
			users = []
			users.append(User.objects.get(pk=userId))
		else:
			users = getBidders(auctionId)
		
		for user in users:
			profile = UserProfile.objects.get(user = user)
			if user.is_active and profile.email_only:
				
				if user.email:
					emailData={}
					emailData["auction"]= auction
					emailData["user"] = user
					emailData["winningBids"] = winningBids	
					msg = getEmailMessage(user.email,"Winning Bids for Auction: " + auction.name,{"data":emailData}, "winningBidsEmail")
					messages.append(msg)
					emailList.append(user.email)

				else:
					noEmailList.append(int(user.id))

		logger.error("sending emails to: %s" % emailList)
		logger.error("user ids without email: %s" % noEmailList)
		data["emailList"] =  emailList
		data["problemEmails"] = noEmailList
		sendBulkEmail(messages)
	except Exception as e:
		logger.error("error sending new user emails: %s" % e)
		return HttpResponse(json.dumps({"success":False, "data": data}), content_type="application/json")

	return HttpResponse(json.dumps({"success":True}), content_type="application/json")

@staff_member_required
def filterAdminIndex(request):
	data = {}
	data["page"] = request.GET.get("page")
	data["nextPage"] = request.GET.get("nextPage")
	data["user"] = request.GET.get("user", False)
	data["auction"] = request.GET.get("auction", False)
	data["invoice"] = request.GET.get("invoice", False)
	data["flat"] = request.GET.get("flat", False)
	auctionId = request.GET.get("auctionId", None)
	data["auctionId"] = auctionId

	if data["auction"]:
		data["auctions"]=Auction.objects.all().order_by("-id")
		if data["user"]:
			data["users"]=User.objects.filter(userInvoice__isnull=False, userInvoice__auction=auctionId)

	else:
		if data["user"]:
			data["users"]=User.objects.all()
	

	if data["invoice"]:
		
		data["invoices"] = Invoice.objects.filter(auction = auctionId)
		#logger.error(data["invoices"])

	if request.method == 'POST':
		try:
			index = request.POST.get("userId")
			
			
			data["success"]=True
			return HttpResponse(json.dumps({"success":True}), content_type="application/json")

		except Exception as e:
			data["success"]=False
			data["errorMsg"] = e
			logger.error("error updating lot ids: %s" % e)
			return render_to_response('admin/audio/filterAdminIndex.html', {"data":data}, context_instance=RequestContext(request))



	return render_to_response('admin/audio/filterAdminIndex.html', {"data":data}, context_instance=RequestContext(request))


@staff_member_required
def adjustLotIds(request, auctionId):
	data={}
	data["auction"]=Auction.objects.get(pk=auctionId)
	
	if request.method == 'POST':
		try:
			index = request.POST.get("index")
			order = request.POST.get("order")
			if not index or not order:
				raise Exception("You must specify index and order.")
			adjustLotIdsUtil(auctionId, index, (order=="up"))
			data["success"]=True
		except Exception as e:
			data["success"]=False
			data["errorMsg"] = e
			logger.error("error updating lot ids: %s" % e)
			return render_to_response('admin/audio/adjustLotIds.html', {"data":data}, context_instance=RequestContext(request))



	return render_to_response('admin/audio/adjustLotIds.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def itemPrintOut(request, auctionId):
	data ={}
	cats = Category.objects.filter(itemCategory__auction = auctionId).distinct()
	for cat in cats:
		items = Item.objects.filter(auction = auctionId, category = cat).order_by("lot_id")
		
		if cat in data:
			data[cat.name] =  items
		else:
			data[cat.name] =  {}
			data[cat.name] =  items
	return render_to_response('admin/audio/itemPrintOut.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def setDiscount(request, invoiceId):
	data ={}
	data["invoice"] = Invoice.objects.get(pk=invoiceId)

	if request.method == 'POST':
		try:
			form = InvoiceForm(request.POST, instance = data["invoice"])
			if form.is_valid():
				form.save()
				data["success"]=True
		except Exception as e:
			data["success"]=False
			data["errorMsg"] = e
			logger.error("error updating invoice %s: %s" % (invoiceId, e))
			return render_to_response('admin/audio/setDiscount.html', {"data":data}, context_instance=RequestContext(request))


	data["form"] = InvoiceForm(instance = data["invoice"])

	
	return render_to_response('admin/audio/setDiscount.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def addItemPrepop(request):
	data = {}
	data["form"] = ItemPrePopulateForm()
	return render_to_response('admin/audio/addItemEntry.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def addItem(request):
	data = {}
	initData = {}
	success = request.GET.get('success', False)
	auction = request.GET.get('auction', None)
	label = request.GET.get('label', None)
	min_bid = request.GET.get('min_bid', None)
	item_type = request.GET.get('item_type', None)
	artist = request.GET.get('artist', None)
	name = request.GET.get('name', None)
	condition = request.GET.get('condition', None)
	category = request.GET.get('category', None)
	lotId = request.GET.get('beginning_lot_id', 0)
	lastLotId = request.GET.get('last_lot_id', 0)

	if lotId == 0:
		lotIds = (Item.objects.filter(auction=auction).order_by('-lot_id').values_list('lot_id', flat=True).distinct())
		if len(lotIds)>0:
			lotId = lotIds[0]
			lastLotId = lotId
			lotId = lotId + 1
	initData = {"auction":auction, "label":label, "min_bid": min_bid, "category": category, "artist": artist, "lot_id" : lotId, "name":name, "condition":condition, "item_type":item_type}
	form = ItemForm(initial = initData)

	if request.method == 'POST':
		try:
			auctionObj = Auction.objects.get(pk=auction)
			if auctionObj.flat_locked:
				logger.error("Auction %s is locked" % auction)
				data["errorMsg"] = "This auction is locked"
				return render_to_response('admin/audio/addItem.html', {"data":data, "success": False, "lastLotId":lastLotId, "nextLotId":lotId, "auctionEnded":True}, context_instance=RequestContext(request))
			

			form = ItemForm(request.POST)

			if form.is_valid():
				item = form.save()
				lotId = int(form.data["lot_id"]) + 1
				lastLotId =  form.data["lot_id"]
				initData["lot_id"] = lotId
				
			else:
				data["form"] = form
				return render_to_response('admin/audio/addItem.html', {"data":data, "success": False, "lastLotId":lastLotId, "nextLotId":lotId}, context_instance=RequestContext(request))
			
			
			data["form"] = ItemForm(initial = initData)
			logger.error("lotId: %s  last_lot_id: %s" % (lotId, lastLotId))
			return render_to_response('admin/audio/addItem.html', {"data":data, "success": True, "lastLotId":lastLotId, "nextLotId":lotId}, context_instance=RequestContext(request))
			
		except Exception as e:
			logger.error("error creating item: %s" % e)
			return render_to_response('admin/audio/addItem.html', {"data":data, "success": False}, context_instance=RequestContext(request))
			
	data["form"] = form
	return render_to_response('admin/audio/addItem.html', {"data":data, "success": success, "lastLotId":lastLotId, "nextLotId":lotId}, context_instance=RequestContext(request))

@staff_member_required
def printLetters(request, template, auctionId=None):
	data = {}
	#profiles = UserProfile.objects.filter(quiet=False, user__is_staff=False, email_only=False, deadbeat=False).order_by("user__last_name")
	num = [1092, 1110, 1144, 1125, 1153, 1136, 1198, 1199, 1207, 1181, 1182, 1234, 1244, 1242, 1233, 1214, 1232, 1228, 1213, 1273, 1267, 1320, 1334, 1380, 1372, 1368, 1364, 1355, 1412, 1406, 1415, 1421, 1433, 1397, 1403, 1413, 1470, 1481, 1479, 1474, 1447, 1464, 1525, 1520, 1492, 1537, 1557, 1568, 1567, 1555, 1605, 1613, 1599, 1626, 1647, 1661, 1641, 1638, 1692, 1669, 1686, 1697, 1713, 1744, 1743, 1774, 1789, 1759, 1821, 1804, 1798, 1877, 1862, 1857, 1875, 1876, 1866, 1914, 1910, 1893, 1895, 1905, 1968, 1970, 1940, 1952, 2010, 2003, 2006, 1994, 1992, 1999, 2043, 2032, 2041, 2092, 2073, 2089, 2064, 2077, 2114, 2149, 2122, 2150, 2130, 2154, 1634]
	profiles = UserProfile.objects.filter(user__in=set(num)).order_by("user__last_name")
	
	#profiles = UserProfile.objects.filter(id__gt=9)
	updated = []
	for profile in profiles:
		user = profile.user

		emailData = {}
		emailData["password"] = user.username + str(profile.id)
		emailData["profile"] = profile 
		updated.append(emailData)

	
	data["profiles"] = updated
	return render_to_response('admin/audio/coverLetter.html', {"data":data, "success": False}, context_instance=RequestContext(request))


@staff_member_required
def printLabels(request, auctionId, labelType=None):
	data = {}
	if labelType:
		if labelType == "NonActive":
			users, addresses = getNonActiveUsers(auctionId)
		if labelType == "Current":
			users, addresses = getCurrentUsers(auctionId)
			
		if labelType == "New":
			users, addresses = getNewUsers()
			
		if labelType == "NonCurrent":
			users, addresses = getNonCurrentUsers(auctionId)

		if labelType == "Courtesy":
			users, addresses = getCourtesyBidders()
		if labelType == "custom":
			
			num = [1092, 1110, 1144, 1125, 1153, 1136, 1198, 1199, 1207, 1181, 1182, 1234, 1244, 1242, 1233, 1214, 1232, 1228, 1213, 1273, 1267, 1320, 1334, 1380, 1372, 1368, 1364, 1355, 1412, 1406, 1415, 1421, 1433, 1397, 1403, 1413, 1470, 1481, 1479, 1474, 1447, 1464, 1525, 1520, 1492, 1537, 1557, 1568, 1567, 1555, 1605, 1613, 1599, 1626, 1647, 1661, 1641, 1638, 1692, 1669, 1686, 1697, 1713, 1744, 1743, 1774, 1789, 1759, 1821, 1804, 1798, 1877, 1862, 1857, 1875, 1876, 1866, 1914, 1910, 1893, 1895, 1905, 1968, 1970, 1940, 1952, 2010, 2003, 2006, 1994, 1992, 1999, 2043, 2032, 2041, 2092, 2073, 2089, 2064, 2077, 2114, 2149, 2122, 2150, 2130, 2154, 1634]
			profiles = UserProfile.objects.filter(user__in=set(num)).order_by("user__last_name")
	


		data["profiles"] = profiles	
	else:
		users, addresses = getNonActiveUsers(auctionId)
		data["profiles"] = profiles

	data["auctionId"]=auctionId
		
	return render_to_response('admin/audio/printLabels.html', {"data":data, "success": False}, context_instance=RequestContext(request))

@staff_member_required
#send email after importing user from csv
def importUserEmail(request):
	data = {}

	if request.method == 'POST':
		messages = []
		emailList = []
		noEmailList = []
		#pull only auth user ids greater than this.  Will most likely be the first user's id that was imported 
		firstId = 2009
		try:
			users = User.objects.filter(id__gte=firstId)
			for user in users:
				profile = UserProfile.objects.get(user = user)
				if notExcluded(profile):
					
					if user.email:
						emailData={}
						emailData["user"] = user
						emailData["password"] = user.username + str(profile.id)	
						emailData["url"] = "http://thoseoldrecords.com/audio/accounts/confirm/" + str(profile.confirmation_code) + "/" + user.username
						msg = getEmailMessage(user.email,"Welcome to Hawthorn's Antique Audio!",{"data":emailData}, "newSystem")
						messages.append(msg)
						emailList.append(user.email)

					else:
						noEmailList.append(int(user.id))

			logger.error("sending emails to: %s" % emailList)
			logger.error("user ids without email: %s" % noEmailList)
			data["emailList"] =  emailList
			data["problemEmails"] = noEmailList
			logger.info("length emails : %s" % str(len(messages)))
			#sendBulkEmail(messages)
		except Exception as e:
			logger.error("error sending new user emails: %s" % e)
			return HttpResponse(json.dumps({"success":False, "data": data}), content_type="application/json")

	return HttpResponse(json.dumps({"success":True, "data": data}), content_type="application/json")

@staff_member_required
def importAdmin(request):
	data = {}
	
	if request.method == 'POST':
		data["problemEmails"] = importUserCSV(request)
		return HttpResponse(json.dumps({"success":True, "data": data}), content_type="application/json")

	return render_to_response('admin/audio/importUsers.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def importUserCSV(request):
	data = {}
	i=0
	errors={}
	with open("/home/kirami/webapps/dev/hawthorn/HAA-addresses-fixed.csv") as f:
		reader = csv.reader(f)
		for row in reader:

			if i>0:
				try:
					
					zip = row[0]
					address1 = row[1]
					address2=row[2]
					cell_phone=row[3]
					city=row[4]
					country=row[5]
					courtesy_list=row[6]
					currentAuction=row[7]
					deadbeat=row[8]
					dpf=row[9]
					email=row[10]
					fax=row[11]
					firstAuction=row[12]
					firstName=row[13]
					history=row[14]
					lastName=row[15]
					notes=row[16]
					pdf=row[17]
					pc=row[18]
					printed_list=row[19]
					provence=row[20]
					state=row[21]
					telephone=row[22]
			
					password = User.objects.make_random_password()
					if i>0:
						
						if not email or len(email) > 30:
							user,created = User.objects.get_or_create(username=firstName+lastName)	
							if not created:
								logger.info("User username NOT created but retrieved: %s" % firstName+lastName)

						else:
							user,created = User.objects.get_or_create(email=email)
							user.username=email 
							if not created:
								logger.info("User email NOT created but retrieved: %s" % email)
					
						
						user.set_password(password)
						if firstName:
							user.first_name = firstName
						if lastName:
							user.last_name = lastName

						user.save()
						
						
						profile, created = UserProfile.objects.get_or_create(user = user)
						if profile.billing_address:
							addressObj = profile.billing_address
						else:
							addressObj = Address.objects.create()
						#logger.error("profile: %s" % profile)
						if zip:
							addressObj.zipcode = zip
						if address1:
							addressObj.address_one = address1
						if address2:
							addressObj.address_two = address2
						if cell_phone:
							addressObj.telephone= cell_phone
						if city:
							addressObj.city = city
						
						if state:
							addressObj.state = state
						if telephone and not cell_phone:
							addressObj.telephone = telephone
						if provence:
							addressObj.provence = provence
						if fax:
							addressObj.fax = fax
						if not country or country=="":
							country = "USA"
						else: 
							country = country.title()
						
						addressObj.country = country
						#logger.error("country %s" % country)
						#logger.error("address country: %s" % addressObj.country)
						if pc:
							addressObj.postal_code = pc
						addressObj.save()
						profile.shipping_address = addressObj
						profile.billing_address = addressObj
						confirmation_code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(33))
						profile.confirmation_code = confirmation_code

						if pdf=="T":
							profile.pdf_list = True
						else:
							profile.pdf_list = False
							if printed_list == "F":
								profile.quiet = True



						profile.pdf_list = True if pdf=="T" else False
						profile.courtesy_list = True if courtesy_list=="T" else False
						profile.deadbeat = True if deadbeat=="T" else False

			
						if not email:
							profile.email_only = False 
						else:
							profile.email_only = True 
						
						if notes:
							profile.notes = notes
						profile.save()

						

				except Exception as e:
					
					logger.error("Error creating user: %s" % e)
					errors[i]=email +" "+ firstName+lastName
					return errors
			i=i+1
	
	logger.error("These users had issues: %s" % errors)
	
	return errors

@staff_member_required
def createUser(request):
	data = {}
	form = None
	#logger.error(request)
	if request.method == 'POST':
		
		form = UserCreateForm(request.POST)

		if form.is_valid():
			user = form.save()
			#user = User.objects.get(email="")
			password = User.objects.make_random_password()
			user.set_password(password)
			
			user.save()

			up = UserProfile.objects.get(user = user)
			up.verified = True
			up.save()
			
			#create address object for them.
			"""
			newAddress = Address.objects.create()
			up = UserProfile.objects.get(user = user)
			up.shipping_address = newAddress
			up.billing_address = newAddress
			up.save()
			"""

			sendEmailMsg = request.POST.get("sendEmail")
			if sendEmailMsg:
				try:
					emailData={}
					emailData["user"] = user
					emailData["password"] = password
					#emailData["url"] = password		
					msg = getEmailMessage(user.email,"Welcome to Hawthorn's Antique Audio!",{"data":emailData}, "newUser")
					sendEmail(msg)

					#send_registration_confirmation(user)
				except Exception as e:
					logger.error("error sending new user email: %s" % e)
					return render_to_response('admin/audio/createUser.html', {"data":data, "success": False, "msg":e}, context_instance=RequestContext(request))
	
			else:
				logger.error("no email sent to: %s" % user.email)
			
			data["form"] = form
			return render_to_response('admin/audio/createUser.html', {"data":data, "success": True}, context_instance=RequestContext(request))
		else:
			data["form"] = form
			return render_to_response('admin/audio/createUser.html', {"data":data, "success": False}, context_instance=RequestContext(request))
	else:
		logger.error("not post")

	
	data["form"] = UserCreateForm()
	return render_to_response('admin/audio/createUser.html', {"data":data}, context_instance=RequestContext(request))


@staff_member_required
def shippingByInvoiceFlat(request, auctionId):
	data = {}
	data["auctionId"] = auctionId
	auction = Auction.objects.get(pk=auctionId)
	data["invoices"] = {}
	winners = getAlphaWinners(auctionId)
	
	if request.method == "POST":
		d = request.POST
		invoiceId = d.get("invoiceId")
		shipping = d.get("shippingAmount")
		logger.error("shipping: %s , invoice: %s" % (shipping, invoiceId))
		try:
			invoice = Invoice.objects.get(id = invoiceId)
			invoice.second_chance_shipping = shipping
			invoice.save()
		except:
			return HttpResponse(json.dumps({"success":False, "invoiceId":invoiceId}), content_type="application/json")

		return HttpResponse(json.dumps({"success":True, "invoiceId":invoiceId}), content_type="application/json")



	for winner in winners:
		
		winnersFlatSum = getWinnerFlatSum(auctionId, userId = winner.id, date=auction.end_date)
		logger.error(winnersFlatSum)
		#if bought flat items
		if winnersFlatSum["sum"] != 0:
			winnersSum = getWinnerSum(auctionId, userId = winner.id, date=auction.end_date)

			invoices = Invoice.objects.filter(auction = auctionId, user_id = winner.id)
			logger.error(invoices)
			if len(invoices) > 0:
				invoice = invoices[0]
				
				data["invoices"][str(invoice.id)] = {}
				data["invoices"][str(invoice.id)]["bids"] = winnersSum
				data["invoices"][str(invoice.id)]["flatBids"] = winnersFlatSum
				data["invoices"][str(invoice.id)]["shipping"] = invoice.shipping 
				data["invoices"][str(invoice.id)]["shipping_two"] = invoice.second_chance_shipping

	return render_to_response('admin/audio/shippingByInvoiceFlat.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def shippingByInvoiceFiltered(request, auctionId):
	return shippingByInvoice(request, auctionId, True)
	
@staff_member_required
def shippingByInvoice(request, auctionId, filter=None):
	
	data = {}
	data["auctionId"] = auctionId
	auction = getCurrentAuction()
	if filter:
		data["filtered"]=True
	else:
		data["filtered"]=False
	
	if request.method == "POST":
		d = request.POST
		invoiceId = d.get("invoiceId")
		shipping = d.get("shippingAmount")
		#logger.error("shipping: %s , invoice: %s" % (shipping, invoiceId))
		try:
			invoice = Invoice.objects.get(id = invoiceId)
			invoice.shipping = shipping
			invoice.save()
		except:
			return HttpResponse(json.dumps({"success":False, "invoiceId":invoiceId}), content_type="application/json")

		return HttpResponse(json.dumps({"success":True, "invoiceId":invoiceId}), content_type="application/json")


	data["invoices"] = {}
	winners = getAlphaWinners(auctionId)
	

	firstInvoice = None

	for winner in winners:
		address = None
		addresses = Address.objects.filter(upShipping__user = winner.id)
		if len(addresses)  < 1:
			logger.error("shippingByInvoice() user %s doesn't have an address on file" % winner.id)
		else:
			address = addresses[0]
		
		if filter:
			invoices = Invoice.objects.filter(auction = auctionId, user_id = winner.id, shipping=0)
		
		else:
			invoices = Invoice.objects.filter(auction = auctionId, user_id = winner.id)
		
		if len(invoices) > 0:
			invoice = invoices[0]
			
			winnersSum = getWinnerSum(auctionId, userId = winner.id)
			data["invoices"][str(invoice.id)] = {}
			data["invoices"][str(invoice.id)]["bids"] = winnersSum
			data["invoices"][str(invoice.id)]["shipping"] = invoice.shipping 
			data["invoices"][str(invoice.id)]["shipping_two"] = invoice.second_chance_shipping
			if address:
				data["invoices"][str(invoice.id)]["country"] = address.country
			
			if firstInvoice != None:
				firstInvoice = invoice.id
	data["firstInvoice"] = firstInvoice
	return render_to_response('admin/audio/shippingByInvoice.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def getPaidUnshipped(request, auctionId):
	data = {}
	data["invoices"] = {}
	data["auction"] = Auction.objects.get(pk = auctionId)
	winners = User.objects.filter(bidUser__item__auction = auctionId, bidUser__winner=True, paymentUser__invoice__auction=auctionId).distinct().order_by("last_name")
	#firstInvoice = None
	for winner in winners:
		address = None
		addresses = Address.objects.filter(upShipping__user = winner)
		if len(addresses)  < 1:
			logger.error("shippingByInvoice() user %s doesn't have an address on file" % winner.id)
		else:
			address = addresses[0]

		invoices = Invoice.objects.filter(auction = auctionId, user_id = winner.id)
		
		if len(invoices) > 0:
			invoice = invoices[0]
			if not invoice.shipped_date:
				winnersSum = getWinnerSum(auctionId, userId =winner.id)
				data["invoices"][str(invoice.id)] = {}
				data["invoices"][str(invoice.id)]["bids"] = winnersSum
				data["invoices"][str(invoice.id)]["subTotal"] = invoice.invoiced_amount + invoice.tax + invoice.second_chance_tax  + invoice.second_chance_invoice_amount - invoice.discount
				data["invoices"][str(invoice.id)]["estimatedShipping"] = invoice.shipping + invoice.second_chance_shipping
				data["invoices"][str(invoice.id)]["total"] = data["invoices"][str(invoice.id)]["subTotal"] + data["invoices"][str(invoice.id)]["estimatedShipping"]
				data["invoices"][str(invoice.id)]["payment"] = getPaymentInfoByUser(winner.id, auctionId = auctionId)
				
				#data["invoices"][str(invoice.id)]["shipping_two"] = invoice.second_chance_shipping
				if address:
					data["invoices"][str(invoice.id)]["address"] = address
				
			#if firstInvoice != None:
				#firstInvoice = invoice.id
	#data["firstInvoice"] = firstInvoice
	return render_to_response('admin/audio/paidNotShipped.html', {"data":data}, context_instance=RequestContext(request))


@staff_member_required
def markShipped(request, auctionId):
	data = {}
	data["invoices"] = {}
	data["auction"] = Auction.objects.get(pk = auctionId)
	
	if request.method == "POST":
		logger.debug(request.POST)

		try:
			date = request.POST.get("shipped_date", None)
			if not date:
				data["errorMsg"] = "You must specify a date"
			else:
				for req in request.POST:
				
					if "invoice" in req:
						invoiceNum = req[8:]
						invoice = Invoice.objects.get(pk=invoiceNum)
						invoice.shipped_date = date
						invoice.save()

				data["success"] = True

		except Exception as e:
			logger.error("Error in markShipped %s" % e)

	winners = User.objects.filter(bidUser__item__auction = auctionId, bidUser__winner=True, paymentUser__invoice__auction=auctionId).distinct().order_by("last_name")
	data["invoices"] = Invoice.objects.filter(user__in=set(winners), shipped_date = None, auction = auctionId).distinct()

	return render_to_response('admin/audio/markShipped.html', {"data":data}, context_instance=RequestContext(request))


@staff_member_required
def emailAdmin(request, auctionId):
	data = {}
	return render_to_response('admin/audio/sendEmailsAdmin.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def createBid(request, auctionId):
	data = {}
	
	if request.method == "POST":
		form = AdminBidForm(auctionId, request.POST)
		if form.is_valid():
			form.save(auctionId = auctionId)
			data["form"] = form
			return render_to_response('admin/audio/createBid.html', {"data":data, "success": True}, context_instance=RequestContext(request))
		else:
			data["form"] = form
			return render_to_response('admin/audio/createBid.html', {"data":data, "error": True}, context_instance=RequestContext(request))
				

	data["form"] = AdminBidForm(auctionId = auctionId)
	data["auction"] = Auction.objects.get(pk = auctionId)
	return render_to_response('admin/audio/createBid.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def endBlindAuction(request, auctionId):
	invoices = {}
	
	#make sure to do all manual stuff first
	auction = Auction.objects.get(id = auctionId)
	now = datetime.now()

	if auction.blind_locked == True:
		return HttpResponse(json.dumps({"success":False, "msg":"This auction is locked"}), content_type="application/json")

	if now < auction.end_date:
		return HttpResponse(json.dumps({"success":False, "msg":"The blind auction time isn't up."}), content_type="application/json")

	#reset then mark winners
	resetWinners(auction.id)
	markWinners(auction.id)
	
	#get all won items before end date
	winners = getWinningBids(auctionId, date = auction.end_date)
	
	for winner in winners:
		userId = winner.user_id
		#logger.error("winner: %s" % winner)
		if userId not in invoices:
			#logger.error( "user not in invoices")
			user = User.objects.get(id = userId)
			address = Address.objects.get(upBilling__user = userId)

			sum = getWinnerSum(auctionId, userId, date = auction.end_date)
			invoicedAmount = sum["sum"]
			#add tax if in CA
			tax = None
			existingInvoices = Invoice.objects.filter(user = user, auction = auction)
			#existingInvoices = Invoice.objects.get_or_create(user = user, auction = auction)	
			if len(existingInvoices) < 1:
				invoice = Invoice.objects.create(user = user, auction = auction, invoiced_amount = invoicedAmount)
			else:
				invoice = existingInvoices[0]
			if address.state == "CA":

				tax = float(invoicedAmount) * settings.CA_TAX
				logger.error("amount:%s tax:%s total:%s" % (invoicedAmount, settings.CA_TAX, tax))
				invoice.tax = tax

			invoice.invoiced_amount = invoicedAmount 
			#invoice.invoice_date = datetime.now()
			invoice.save()
			



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

#admin page for ending user's flat auction
@login_required
def endSSAuction(request, auctionId, userId = None):
	data = {}
	data["auction"] = Auction.objects.get(pk=auctionId) 
	invoice = None
	
	invoices = Invoice.objects.filter(user = userId, auction=auctionId)
	if len(invoices) < 1:
		data["errorMsg"] = "This user doesn't have an invoice, they should not have a Set Sale open."
	else:
		invoice = invoices[0]
		if invoice.second_chance_invoice_amount != 0:
			data["errorMsg"]= "This user already has information saved for second_chance invoice."

	data["user"] = User.objects.get(pk=userId)
	return render_to_response('admin/audio/endSSAuction.html', {"data":data}, context_instance=RequestContext(request))


@login_required
def endFlatAuction(request, auctionId, userId = None):
	logger.error("user %s" % request.user)
	if userId:
		logger.error("userId:%s logged in:%s" %(userId, request.user.id))
		if int(userId) != int(request.user.id) and not request.user.is_staff:
			logger.error("Tried to end Flat Auction with bad user: %s" % request.user)
			return HttpResponse(json.dumps({"success":False, "msg":"Something went wrong.  Please contanct us."}), content_type="application/json")



	
	data = {}
	data["auction"] =  Auction.objects.get(pk = auctionId)
	data["user"] =  request.user
	now = datetime.now()
	#for all bids in auction not invoiced

	email = request.POST.get("email", True)



	#make sure to do all manual stuff first
	auction = Auction.objects.get(id = auctionId)
	if auction.flat_locked == True and userId == None:
		logger.error("This auction is Set Sale locked")
		return HttpResponse(json.dumps({"success":False, "msg":"This auction is Set Sale locked"}), content_type="application/json")

	if now < auction.second_chance_end_date and not userId:
		logger.error("The Set Sale auction time isn't up.")
		return HttpResponse(json.dumps({"success":False, "msg":"The Set Sale auction time isn't up."}), content_type="application/json")


	#DO NOT mark winners - they should already be marked

	#get all won items before end date

	#winners = getWinningFlatBids(auctionId, onlyNonInvoiced=True, userId = userId)
	winners = getWinningFlatBids(auctionId, date=auction.end_date, userId = userId)
	#logger.error("winners %s"  % winners)
	invoice = None
	for winner in winners:
		winnerId = winner.user_id

		invoices = Invoice.objects.filter(auction=auction, user = winnerId)
		#if no invoice from blind auction, create
		if len(invoices)<1:
			return HttpResponse(json.dumps({"success":False, "msg":"This winner has no invoice, only auction winners should be able to win set sale items."}), content_type="application/json")
			
		else:
			invoice = invoices[0]
			
			if invoice.second_chance_invoice_amount == 0:
				
				sum = getWinnerFlatSum(auctionId, date=auction.end_date, userId = winnerId)
				invoicedAmount = sum["sum"]
				
				invoice.second_chance_invoice_amount = invoicedAmount
				#shipping
				invoice.second_chance_invoice_date = datetime.now()
				address = Address.objects.get(upShipping__user_id = winnerId)
				tax = None
				if address.state == "CA":
					tax = float(invoicedAmount) * .0975
					invoice.second_chance_tax = tax

				invoice.save()
	if userId == None:			
		auction.flat_locked = True
		auction.save()

	if userId and email:
		data["invoice"]=invoice
		data["user"] = User.objects.get(pk=userId)
		msg = getEmailMessage(settings.DEFAULT_FROM_EMAIL ,"User ended Set Sale Auction",{"data":data}, "endSetSaleAuction", False)
		msg.send()	

	if int(userId) == int(request.user.id):
		logger.error("sending invoice")
		sendInvoices(request, auction.id, userId)

	
	return HttpResponse(json.dumps({"success":True}), content_type="application/json")

@staff_member_required
def userBreakdown(request, auctionId = None):
	data = {}
	auction = None

	data["includeEbay"] = request.GET.get("includeEbay", False)
	data["excludePDF"] = request.GET.get("excludePDF", False)
	data["excludeEmailOnly"] = request.GET.get("excludeEmailOnly", False)
	data["excludePrintedNotices"] = request.GET.get("excludePrintedNotices", False)
	
	if not auctionId:
		auction = getCurrentAuction()
		if not auction:
			auction = Auction.objects.latest('start_date')
			auctionId = auction.id
		else:
			auctionId = auction.id	
	else:
		auction = Auction.objects.get(pk=auctionId)

	data["new"] = getNewUsers(auction)
	data["current"] = getCurrentUsers(auctionId, excludeEmailOnly = data["excludeEmailOnly"], excludePDF = data["excludePDF"], excludeEbay = not data["includeEbay"], excludePrintedNotices = data["excludePrintedNotices"])
	data["nonCurrent"] = getNonCurrentUsers(auctionId)
	data["nonActive"] = getNonActiveUsers(auctionId)
	data["courtesy"] = getCourtesyBidders()

	data["auctionId"]=auctionId

	return render_to_response('admin/audio/userBreakdown.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def endAuction(request, auctionId):
	data = {}
	data["auctionId"]=auctionId

	auction = Auction.objects.get(id=auctionId)
	if auction.flat_locked:
		data["flat_locked"] = True
	if auction.blind_locked:
		data["blind_locked"] = True


	return render_to_response('admin/audio/endAuction.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def invoices(request, auctionId):
	data = {}
	auctions = Auction.objects.filter(pk=auctionId)
	if len(auctions) < 1:
		data["error"]=True
		data["errorMsg"] = "Auction #"+auctionId+" doens't exist"
	else:
		data["auction"] = auctions[0]
	return render_to_response('admin/audio/invoiceAdmin.html', {"data":data}, context_instance=RequestContext(request))

def notExcluded(up, emailOnly=False):
	if emailOnly:
		return not up.quiet and not up.deadbeat and up.email_only
	else:	
		return not up.quiet and not up.deadbeat



@staff_member_required
def sendLoserLetters(request, auctionId):
	losers = getLosers(auctionId)
	messages = []
	template = "loserLetter"
	data = {}
	data["auction"] = Auction.objects.get(pk = auctionId)
	#logger.error("losers:")
	for loser in losers:

		data["winningBids"] = getWinningBidsFromLosers(auctionId, user.id)
		data["profile"] = loser
		if notExcluded(loser, emailOnly = True):
			msg = getEmailMessage(user.email,"Hawthorn Antique Audio Auction results",{"data":data}, template, False)
			messages.append(msg)

	if template :
		logger.error("sending msgs ")
		sendBulkEmail(messages)
		return HttpResponse(json.dumps({"success":True}), content_type="application/json")

	
	return HttpResponse(json.dumps({"success":True}), content_type="application/json")

@staff_member_required
def getInvoices(request, auctionId, userId = None, printIt = None):
	invoiceTemplate = "admin/audio/printInvoice.html" if printIt else "admin/audio/invoice.html"
	try:
		data = {}
		if userId != None:
			data = getInvoiceData(auctionId, userId)
			getHeaderData(data, auctionId)
	except Exception as e:
		logger.error("Error in getInvoices: %s" % e)	
	return render_to_response(invoiceTemplate, {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def printInvoices(request, auctionId, userId = None):
	
	try:
		filter = request.GET.get("filter", False)
		data = {}
		
		data["auction"] = Auction.objects.get(pk=auctionId)
		data["flat"] = request.GET.get("flat", False)
		data["invoices"] = {}
		if userId != None:
			data["invoices"][str(userId)] = getInvoiceData(auctionId, userId)
			data["invoices"][str(userId)]["profile"] = UserProfile.objects.get(user = userId)
			#save invoice date as today
			invoice = data["invoices"][str(winner.id)]["invoice"]
			if data["flat"]:
				invoice.second_chance_invoice_date = datetime.now()
			else:
				invoice.invoice_date = datetime.now()
		else:
			if filter:
				if data["flat"]:
					winners = getWinningFlatBids(auctionId, date=data["auction"].end_date, userId = userId)
				else:
					winners = getAlphaWinners(auctionId, True)
	
			else:
				if data["flat"]:
					winners = getWinningFlatBids(auctionId, date=data["auction"].end_date, userId = userId)
				else:
					winners = getAlphaWinners(auctionId)

			#logger.error("winners: %s"  % winners)
			for winner in winners:
				data["invoices"][str(winner.id)] = getInvoiceData(auctionId, winner.id)
				data["invoices"][str(winner.id)]["profile"] = UserProfile.objects.get(user = winner.id)
				#save invoice date
				invoice = data["invoices"][str(winner.id)]["invoice"]
				if data["flat"]:
					invoice.second_chance_invoice_date = datetime.now()
				else:
					invoice.invoice_date = datetime.now()
		
		getHeaderData(data, auctionId)
		

	except Exception as e:
		logger.error("Error in printInvoices: %e" % e)	
	return render_to_response("admin/audio/printInvoice.html", {"data":data}, context_instance=RequestContext(request))

@login_required
def sendInvoices(request, auctionId = None, userId = None):
	if not auctionId:
		auctionId = request.POST.get("auctionId")
	if not userId:
		userId = request.POST.get("userId", None)
	auction = Auction.objects.get(id = auctionId)
	
	winners = {}
	messages = []
	data = {}
	subject = "Invoice for Hawthorn's Antique Audio"
	isFlat = False
	data["auction"] = auction

	if not auction.blind_locked:
		return HttpResponse(json.dumps({"success":False, "msg":"This auction has not been locked.  Please make sure to lock the auction before trying to send invoices."}), content_type="application/json")

	if auction.flat_locked:
		subject = "Updated invoice for Hawthorn's Antique Audio"
		isFlat = True
		winners = getWinningFlatBids(auction.id, date=auction.end_date, userId = userId)
	else:
		if userId == None:
			if not request.user.is_staff:
				return HttpResponse(json.dumps({"success":False, "msg":"Mass invoice email trying to be send from non staffer."}), content_type="application/json")
			winners = getAlphaWinners(auctionId)
		else:
			winners = [User.objects.get(pk=userId)] 	


	data["isFlat"] = isFlat

	for winner in winners:
		profile = UserProfile.objects.get(user_id = winner.id)
		if profile and profile.email_only:
			#logger.error("winner: %s" % winner.id)
			
			data = getInvoiceData(auctionId, winner.id)
			#logger.error("userId %s" % userId)
			if userId:
				if data["invoice"].second_chance_invoice_amount > 0:
					data["isFlat"] = True	
					data["invoice"].second_chance_invoice_date = datetime.now()

					subject = "Updated invoice for Hawthorn's Antique Audio"
			else:
				if isFlat:
					data["invoice"].second_chance_invoice_date = datetime.now()
				else:
					data["invoice"].invoice_date = datetime.now()

			msg = getEmailMessage(data["user"].email,subject, {"data":data}, "invoice", False)
			messages.append(msg)
				

	sendBulkEmail(messages)
	return HttpResponse(json.dumps({"success":True}), content_type="application/json")



@staff_member_required
def sendReminder(request):
	auctionId = request.POST.get("auctionId")
	userId = request.POST.get("userId", None)
	auction = Auction.objects.get(id = auctionId)
	
	balances = getUnbalancedUsersByAuction()
	balance = 0

	if len(balances) > 0:
		balance = balances[0]["iSum"] - balances[0]["pSum"]
	
	messages = []
	data = {}
	data["auction"] = auction

	#if not auction.blind_locked:
	#	return HttpResponse(json.dumps({"success":True, "msg":"This auction has not been locked.  Please make sure to lock the auction before trying to send reminders."}), content_type="application/json")

	if userId == None:
		winners = getAlphaWinners(auctionId)
	else:
		winners = [User.objects.get(pk=userId)] 		

	template = "reminder"


	for winner in winners:
		profile = UserProfile.objects.get(user_id = winner.id)
		if profile and profile.email_only:
			user = User.objects.get(id = winner.id)
			data = getInvoiceData(auctionId, userId)
			msg = getEmailMessage(user.email,"Reminder for Hawthorn's Antique Audio Auction: " + auction.name, {"data":data}, template)
			messages.append(msg)
				
		if template :
			sendBulkEmail(messages)
			return HttpResponse(json.dumps({"success":True}), content_type="application/json")

	return HttpResponse(json.dumps({"success":True}), content_type="application/json")
		
@staff_member_required
def sendAllConsignorReports(request):
	d = request.POST
	auctionId = d.get("auctionId")
	#logger.error("auction:")
	#logger.error(auctionId)
	template = "singleConsignorReport"
	return consignorReport(request, auctionId, template)

@staff_member_required
def sendTemplateEmail(request):
	d = request.POST
	consignorId = d.get("consignorId")
	auctionId = d.get("auctionId")
	template = d.get("template")
	return consignorReportById(request, consignorId, auctionId, template)

@staff_member_required
def consignorReportById(request, consignorId, auctionId, template = None):
	data = getAllConsignmentInfo(consignorId, auctionId)	
	getHeaderData(data, auctionId)
	consignor = Consignor.objects.get(id=consignorId)
	
	if template:
		msg = getEmailMessage(consignor.email,"Hawthorn Antique Audio Consignor Report",{"data":data}, template)
		sendEmail(msg)
		return HttpResponse(json.dumps({"success":True}), content_type="application/json")
		

	return render_to_response('admin/audio/consignorReportById.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def consignorReport(request, auctionId, template = None):
	data = {}
	messages = []
	usedConsignors = {}
	consignorTotal = 0
	gross = 0

	try:
		#all consignors, consignor total money
		data["total"] = getSumWinners(auctionId)
		getHeaderData(data, auctionId)
		data["nonWinners"] = getLoserConsignors(auctionId)
		
		consignors = getWinnerConsignors(auctionId = auctionId)
		for consignor in consignors:
			consignorId = consignors
			if consignorId not in usedConsignors:
				#logger.error("consignor: %s" % consignorId)
				consignor = Consignor.objects.get(id = consignorId)
				consignInfo = consignorId
				indData = getAllConsignmentInfo(consignorId, auctionId)
				data[consignInfo] = indData
				usedConsignors[consignorId] = True
				consignorTotal = consignorTotal + indData["consignorTotal"]
				gross = gross + indData["gross"]
				if template:
					msg = getEmailMessage(consignor.email,"Hawthorn Antique Audio Consignor Report",{"data":indData, "header":data}, template)
					messages.append(msg)

		data["consignorTotal"] = consignorTotal
		data["consignedTotal"] = gross
		data["totalHAA"] = float(gross) - consignorTotal 
		if template:

			for nonwinner in data["nonWinners"]:
				
				consignInfo = nonwinner.id
				indData = getAllConsignmentInfo(nonwinner.id, auctionId)
				#logger.error("consignor: %s" % indData)
				data[consignInfo] = indData
				msg = getEmailMessage(nonwinner.email,"Hawthorn Antique Audio Consignor Report",{"data":indData, "header":data}, "noConsignmentWonReport")
				messages.append(msg)


			sendBulkEmail(messages)
			return HttpResponse(json.dumps({"success":True,"msg":"sent bulk emails"}), content_type="application/json")
	except Exception as e:
		logger.error("consignorReport error: %s" % e)		

	return render_to_response('admin/audio/consignorReport.html', {"data":data}, context_instance=RequestContext(request))	


@staff_member_required
def userBalanceInfo(request, userId):
	data = {}

	invoices = getInvoiceInfoByUser(userId)
	data["invoices"] = invoices
	data["payments"] = getPaymentInfoByUser(userId)
	data["remaining"] = invoices["sum"] - data["payments"]["sum"]
	data["user"] = User.objects.get(pk=userId)
	return render_to_response('admin/audio/userBalance.html', {"data":data}, context_instance=RequestContext(request))	

@staff_member_required
def calculateBalances(request, auctionId = None):
	data = {}
	
	#get invoices for this auction?  
	#get unpaid invoices?
	#invoices amount total - paid amount total?
	#
	data["auctions"] = Auction.objects.all().order_by("-id")
	if auctionId:
		data["auction"]= Auction.objects.get(pk=auctionId)
	data["totalPayments"] = getTotalPaymentAmount(auctionId)
	data["totalInvoices"] = getTotalInvoiceAmount(auctionId)
	data["remaining"] = data["totalInvoices"] -data["totalPayments"]

	#per user
	unbalancedUsers = getUnbalancedUsers()
	for user in unbalancedUsers:
		#logger.error("user_id %s" % user["user_id"])
		users = User.objects.filter(pk=user["user_id"])
		if len(users) > 0:
			user["user"] = users[0]

	data["unbalancedUsers"] = unbalancedUsers

	return render_to_response('admin/audio/balances.html', {"data":data}, context_instance=RequestContext(request))	

@staff_member_required
def reportByUser(request):
	data = {}
	auctionId = 1
	data["winningBids"] = getWinningBids(auctionId, userId = 1)
	return render_to_response('admin/audio/winners.html', {"data":data}, context_instance=RequestContext(request))	


@staff_member_required
def getRunningBidTotal(request, auctionId):
	data = {}
	data["auction"] = Auction.objects.get(pk=auctionId)
	dupes = getDuplicateItems(auctionId)
	bids = getOrderedBids(auctionId)
	currentItemId = 0
	index = 0
	total = 0
	#logger.error("bids: %s" % bids)
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

		if index < quantity:
			total = total + bid.amount
			#logger.error("bid: %s total: %s"  % (bid.amount, total))
		
		index = index + 1
	data["total"] = total
	return render_to_response('admin/audio/runningTotal.html', {"data":data}, context_instance=RequestContext(request))	


def markWinners(auctionId):
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

@staff_member_required
def winners(request, auctionId):
	data = {}
	winners = getAlphaWinners(auctionId)
	for winner in winners:
		try:
			#logger.error("winner: " + winner)
			address = Address.objects.get(upShipping__user = winner.id)
			winner["zipcode"] = address.zipcode
		except:
			pass
	
	data["winningBids"] = winners
	getHeaderData(data, auctionId)
	
	return render_to_response('admin/audio/winners.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def losers(request, auctionId):
	data = {}
	getHeaderData(data, auctionId)
	return render_to_response('admin/audio/losers.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def wonItems(request, auctionId):
	data = {}
	getHeaderData(data, auctionId)
	return render_to_response('admin/audio/wonItems.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def unsoldItems(request, auctionId):
	data = {}
	getHeaderData(data, auctionId)
	return render_to_response('admin/audio/unsoldItems.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def bulkConsignment(request, auctionId):
	error = False
	data = {}
	data["auction"] = Auction.objects.get(pk=auctionId)
	try:
		if request.method == 'POST':
			form = BulkConsignment(request.POST, auctionId = auctionId)
			if form.is_valid():			
				new_user = form.save()
				form = BulkConsignment(auctionId = auctionId)

				return render_to_response('admin/audio/bulkConsignment.html', {"form":form, "data":data, "error":error, "success":True}, context_instance=RequestContext(request))
			else:
				return render_to_response('admin/audio/bulkConsignment.html', {"form":form, "data":data}, context_instance=RequestContext(request))

		else:
			form = BulkConsignment(auctionId = auctionId)
	except Exception as e:
		logger.error("error in bulk consignment: %s" %e)
		error = True
	
	return render_to_response('admin/audio/bulkConsignment.html', {"form":form, "error":error, "data": data}, context_instance=RequestContext(request))

@staff_member_required
def runReport(request, auctionId):
 	data = {}
 	getHeaderData(data, auctionId)
 	return render_to_response('admin/audio/report.html', {"data":data}, context_instance=RequestContext(request))

@staff_member_required
def test(request):
	num = [1092, 1110, 1144, 1125, 1153, 1136, 1198, 1199, 1207, 1181, 1182, 1234, 1244, 1242, 1233, 1214, 1232, 1228, 1213, 1273, 1267, 1320, 1334, 1380, 1372, 1368, 1364, 1355, 1412, 1406, 1415, 1421, 1433, 1397, 1403, 1413, 1470, 1481, 1479, 1474, 1447, 1464, 1525, 1520, 1492, 1537, 1557, 1568, 1567, 1555, 1605, 1613, 1599, 1626, 1647, 1661, 1641, 1638, 1692, 1669, 1686, 1697, 1713, 1744, 1743, 1774, 1789, 1759, 1821, 1804, 1798, 1877, 1862, 1857, 1875, 1876, 1866, 1914, 1910, 1893, 1895, 1905, 1968, 1970, 1940, 1952, 2010, 2003, 2006, 1994, 1992, 1999, 2043, 2032, 2041, 2092, 2073, 2089, 2064, 2077, 2114, 2149, 2122, 2150, 2130, 2154, 1634]
	profiles = UserProfile.objects.filter(user__in=set(num))
	for profile in profiles:
		if "@" in profile.user.username and profile.user.email == "":
			profile.user.username = profile.user.first_name + profile.user.last_name 
			profile.email_only = False
			profile.user.save()
			profile.save()
	return HttpResponse(json.dumps({"success":True, "users":str(list(profiles))}), content_type="application/json")

@staff_member_required
#add many test items quickly
def testItemInput(request, index, length):
	i = int(index)
	label = Label.objects.get(pk=1)
	category = Category.objects.get(pk=1)
	auction = Auction.objects.get(pk=8)

	try:
		#logger.error("index:%s,  length :%s" % (index, length))
		while i < int(index) + int(length):
			item = Item.objects.get_or_create(name="N"+str(i), condition = "x", auction  = auction, artist="A"+str(i), min_bid=2.0, label=label, category=category, lot_id = i)
			#logger.error("item: %s" % item)
			i = i +1

		#create test users:



	except Exception as e:
		logger.error("test input error: %s" % e)
		return HttpResponse(json.dumps({"success":False, "msg": e}), content_type="application/json")
	return HttpResponse(json.dumps({"success":True}), content_type="application/json")
