from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import login
from django.contrib.auth import authenticate, login
from django.template import RequestContext, loader
from django.core.mail import send_mail

from audio.forms import ContactForm, BidSubmitForm, UserCreateForm, UserForm

from audio.models import Address, Item, Bid, Auction, UserProfile, Invoice, Category

from datetime import datetime, date  
from audio.utils import *
from audio.mail import *

import logging
import json, math, string, random




# Get an instance of a logger
logger = logging.getLogger(__name__)

def test(request):
	data = {}
	return render_to_response('contact.html', {"data":data}, context_instance=RequestContext(request))


def index(request):
	t = loader.get_template('home.html')
	c = RequestContext(request, {'foo': 'bar'})
	return HttpResponse(t.render(c), content_type="text/html")

def simpleForm(request):
	form = None
	data = None
	now = date.today()
	currentAuction = getCurrentAuction()
	if(request.user.is_authenticated()):
		
		if request.method == "POST":
			try:
				addresses = Address.objects.filter(user=request.user)
				up = UserProfile.objects.get(user = request.user)
				if len(addresses) < 1:
					return render_to_response('item.html', {"form":form, "success": False, "msg":"You must have an address on file to bid."}, context_instance=RequestContext(request))					
				
				if up.deadbeat:
					return render_to_response('item.html', {"form":form, "success": False, "msg":"There is a problem with your account.  Please contact us if you'd like to bid"}, context_instance=RequestContext(request))					
				
				if up.quiet:
					return HttpResponse(json.dumps({"success":False, "msg":"You're set to not receive any contact from us.  To bid please go to your profile and uncheck 'I want no contact' "}), content_type="application/json")	


				form = BidSubmitForm(currentAuction.id, request.POST)
			except:
				return render_to_response('item.html', {"form":form, "success": True}, context_instance=RequestContext(request))
			
			if form.is_valid():
				bid = form.save(commit=False)
				bid.user = request.user
				bid.date = datetime.now()
				try:
					bid.save()
				except Exception as e:
					if e[0] == 1062:
						return render_to_response('item.html', {"form":form, "success": False, "msg":"You've already bid on this item.  Please go to your account to edit/delete"}, context_instance=RequestContext(request))					
				return render_to_response('item.html', {"form":form, "success": True}, context_instance=RequestContext(request))
			else:
				return render_to_response('item.html', {"form":form}, context_instance=RequestContext(request))

		else:
			if isSecondChance() or isBetweenSegments():
				bids = Bid.objects.filter(user=request.user, item__auction=currentAuction, winner=True)
				

				if len(bids) < 1 and isBetweenSegments():
					return render_to_response('noAuction.html', data, context_instance=RequestContext(request))	

					
				elif len(bids) < 1:
					return redirect("noAuction")
				return redirect("flatFeeCatalog")

			if currentAuction == None:
				return redirect("noAuction")

			form = BidSubmitForm(auctionId = currentAuction.id)
	else:
		return redirect("catalog")
	return render_to_response('item.html', {"form":form}, context_instance=RequestContext(request))


@login_required
def accountSettings(request):
	data = {}
	up = UserProfile.objects.get(user = request.user)
	if request.method == "POST":
		try:
			quiet = request.POST.get("quietBox", None)

			if quiet:
				up.quiet = True
			else:
				up.quiet = False
			up.save()
			data["success"] = True
		except:
			data["error"] = True
			return render_to_response('settings.html', {"data":data}, context_instance=RequestContext(request))

	data["quietChecked"] = up.quiet
	return render_to_response('settings.html', {"data":data}, context_instance=RequestContext(request))
		
@login_required	
def contact_info(request):
	data = {}
	billingForm = None
	shippingForm = None
	up = UserProfile.objects.get(user = request.user)
	success = False

	instance = None
	instances = Address.objects.filter(upShipping__user=request.user)
	if len(instances) > 0:
		instance = instances[0]

	billing_instance = None
	billing_instances = Address.objects.filter(upBilling__user=request.user)
	if len(billing_instances) > 0:
		billing_instance = billing_instances[0]


	init = {}
	if not instance:
		init = {"country":"USA"}

	if request.method == 'POST':
		try:
			same = request.POST.get("sameAddress", None)
			shippingForm = ContactForm(request.POST, instance = instance, prefix="shippingForm")	
			
			if same:
				data["sameAddress"] = True
				billingForm = ContactForm( prefix="billingForm", initial={"country":"USA"})

				if shippingForm.is_valid():
					contact = shippingForm.save(commit=True)
					up.shipping_address = contact
					up.billing_address = contact
					success = True
			
			else:
				data["sameAddress"] = False
				billingForm = ContactForm(request.POST, instance = billing_instance, prefix="billingForm")


				if shippingForm.is_valid() and billingForm.is_valid():
					contact = shippingForm.save(commit=True)
					newBilling = billingForm.save(commit=True)
					up.shipping_address = contact
					up.billing_address = newBilling
					success = True


			if success:
				up.save()

			data["shippingForm"] = shippingForm
			data["billingForm"]=billingForm

			return render_to_response('contact.html', {"data":data, "success": success}, context_instance=RequestContext(request))

			
		except Exception as e:
			logger.error("contact_info error: %s" %e)

	#if new instance default country to USA	

	shippingForm = ContactForm(instance=instance, prefix="shippingForm", initial=init)
	if instance and billing_instance == instance:
		billingForm =  ContactForm( prefix="billingForm", initial={"country":"USA"})
	else:
		billingForm = ContactForm(instance=billing_instance, prefix="billingForm", initial=init)

	data["shippingForm"] = shippingForm
	data["billingForm"]=billingForm
	return render_to_response('contact.html', {"data":data}, context_instance=RequestContext(request))


def register(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            nu = authenticate(username=request.POST['username'],
                                    password=request.POST['password1'])
            login(request, nu)
            confirmation_code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(33))
            p = UserProfile.objects.get(user=new_user)
            p.confirmation_code = confirmation_code
            p.save()
            send_registration_confirmation(new_user)
            return HttpResponseRedirect("../profile")
    else:
        form = UserCreateForm()
    return render(request, "registration/register.html", {
        'form': form,
    })


def send_registration_confirmation(user):
	p = UserProfile.objects.get(user=user)
	emailData={}
	emailData["url"] = "http://haa/audio/accounts/confirm/" + str(p.confirmation_code) + "/" + user.username
	emailData["user"]=user
	msg = getEmailMessage(user.email,"Welcome to Hawthorn's Antique Audio!",{"data":emailData}, "verifyEmail")
	sendEmail(msg)


def verifyEmail(request):
	if(request.user.is_authenticated()):
		send_registration_confirmation(request.user)
		data = {}
		data["user"] = request.user
		data["resent"]=True
		logger.error("resent")
		return render_to_response('verified.html', {"data":data}, context_instance=RequestContext(request))
	else:
		return redirect("profile")	

def resetPassword(request):
	
	data = {}
	if request.POST:
		try:
			emailAddress = request.POST.get("email")
			users = User.objects.filter(email = emailAddress)
			if len(users) < 1:
				data["errorMsg"]="That email hasn't been registered with us."
				logger.error("tried to reset unregistered account: %s" % emailAddress)
				return render_to_response('resetPassword.html', {"data":data}, context_instance=RequestContext(request))	
			user = users[0]
			password = User.objects.make_random_password()
			user.set_password(password)
			user.save()
			logger.error("user: %s" %user.email)
			emailData={}
			emailData["user"] = user
			emailData["password"] = password	
			msg = getEmailMessage(user.email,"We received a request to reset your password",{"data":emailData}, "resetPassword")
			sendEmail(msg)
		except Exception as e:
			logger.error("Error reseting password: %s" % e)
			data["errorMsg"]="Something went wrong.  Please contact us."
			return render_to_response('resetPassword.html', {"data":data}, context_instance=RequestContext(request))	
		logger.error("true")
		data["success"]=True
		return render_to_response('resetPassword.html', {"data":data}, context_instance=RequestContext(request))	
	
	return render_to_response('resetPassword.html', {"data":data}, context_instance=RequestContext(request))					

def confirm(request, confirmation_code, username):
	users = UserProfile.objects.filter(user__username=username)
	user = User.objects.get(username = username)
	profile = None
	data = {}
	if len(users)> 0:
		profile = users[0]
		
		if profile.confirmation_code == confirmation_code:
			profile.verified = True
			profile.save()
			#auth_login(request,user)
			verified = profile.verified
		else:
			data["errorMsg"] = "The information you provided is not correct."

	
	data["user"] = user
	return render_to_response('verified.html', {"data":data}, context_instance=RequestContext(request))

@login_required
def bids(request):
	logger.error("bids")
	if(request.user.is_authenticated()):
		currentAuction = getCurrentAuction()
		
		if not currentAuction:
			return redirect('noAuction')

		currentAuctionId = currentAuction.id
		bids = Bid.objects.filter(item__auction = currentAuctionId, user= request.user)
		#logger.error("bids: %s" % bids)
		#logger.error("user: %s" % request.user)

		success = False
		if request.GET.get("success"):
			success = True
		invoices = Invoice.objects.filter(user = request.user, auction = currentAuction.id)
		invoice = None
		if len(invoices) > 0:
			invoice = invoices[0]
			
		if isSecondChance():
			if invoice == None or invoice.second_chance_invoice_amount == 0:
				bids = Bid.objects.filter(item__auction = currentAuctionId, date__gt = currentAuction.end_date, user=request.user)
				
				return render_to_response('flatBids.html', {"success":success, "bids":bids, "endAuctionOption":True, "auctionId":currentAuctionId}, context_instance=RequestContext(request))
			else:
				#They've already ended their auction.  Summary?
					return render_to_response('flatBids.html', {"success":success, "bids":bids, "ended":True, "auctionId":currentAuctionId}, context_instance=RequestContext(request))
			

		else:
			return render_to_response('bids.html', {"success":success,"bids":bids}, context_instance=RequestContext(request))
	else:
		return redirect("profile")

@login_required
def auctionSummaries(request):
	data = {}
	if(request.user.is_authenticated()):
		data["auctions"] = getWonAuctions(request.user.id)
		return render_to_response('auctionSummaries.html', {"data":data}, context_instance=RequestContext(request))
	else:
		return redirect("profile")

@login_required
def auctionSummary(request, auctionId):
	data={}
	if(request.user.is_authenticated()):
		auctions = Auction.objects.filter(id=auctionId)
		
		if len(auctions) < 1:
			return redirect("catalog")
		
		currentAuction = auctions[0]
		
		if isBetweenSegments():
			return redirect("catalog")

		if not currentAuction.blind_locked:
			return redirect("catalog")

		data["auction"] = currentAuction
		data["bids"] = Bid.objects.filter(user = request.user, item__auction = currentAuction, winner = True)

		return render_to_response('endingBids.html', {"data":data}, context_instance=RequestContext(request))
	
	return redirect("catalog")



@login_required
def profile(request):
	data = {}
	if request.user.is_authenticated():
		shipping = Address.objects.filter(upShipping__user=request.user)
		billing = Address.objects.filter(upBilling__user=request.user)
		profile = UserProfile.objects.get(user=request.user)
		data["needVerified"]= not profile.verified
		if len(shipping) < 1 or len(billing) < 1:
			data["addressMsg"]=True
	return render_to_response('profile.html', {"data":data}, context_instance=RequestContext(request))

@login_required
def userInfo(request):
	
	if request.user.is_authenticated():

		if request.method == 'POST':
			form = UserForm(request.POST, instance=request.user)
			if form.is_valid():
				new_user = form.save()
				return render(request, "userInfo.html", {'form': form,})
		else:
			form = UserForm(instance=request.user)
		return render(request, "userInfo.html", {'form': form,})
	else:
		return redirect("profile")


@login_required
def flatFeeCatalog(request):
	items = None
	auction = getCurrentAuction()
	
	success = False
	if request.GET.get("success"):
		success = True

	if request.user.is_authenticated():
		if not isSecondChance() or not auction:
			return redirect("catalog")
		
		try:

			invoices = Invoice.objects.filter(user = request.user, auction = auction)
			invoice = None
			#if user ended their auction and got an invoice
			if len(invoices) > 0:
				invoice = invoices[0]
				if invoice.second_chance_invoice_amount > 0:
					return redirect("auctionSummaries")
				
			bids = Bid.objects.filter(user=request.user, item__auction=auction, winner=True)
			if len(bids) < 1:	
				return redirect("noAuction")
			
			if isBetweenSegments():
				return render_to_response('inBetween.html', data, context_instance=RequestContext(request))	

			items = getNoBidItems(auction.id)
		except Exception as e:
			logger.error("error in catalog")
			logger.error(e)
		
		return render_to_response('flatCatalog.html', {"catItems":items, "auctionId":auction.id, "success":success}, context_instance=RequestContext(request))
	return redirect("profile")


def noAuction(request):
	data = {}
	currentAuction = getCurrentAuction()
	
	if currentAuction:

		if request.user.is_authenticated():
		
			try:
				#if after close but in 2nd chance
				if isSecondChance() or isBetweenSegments():
					#only allow winners to bid (so only add on to won shipments)
					bids = Bid.objects.filter(user=request.user, item__auction=currentAuction, winner=True)
					
					if len(bids) < 1 and isBetweenSegments():
						return render_to_response('noAuction.html', data, context_instance=RequestContext(request))	

					elif len(bids) > 0:	
						
						return redirect("flatFeeCatalog")
				else:
					return redirect("catalog")
			except:
				return render_to_response('noAuction.html', data, context_instance=RequestContext(request))
		elif isSecondChance():
			return render_to_response('noAuction.html', data, context_instance=RequestContext(request))
		
		else: 
			return redirect("catalog")
	return render_to_response('noAuction.html', data, context_instance=RequestContext(request))

def catalogByCategory(request, order):
	data = {}
	currentAuction = getCurrentAuction()
	total = 1
	bidDict = []
	msg = ""
	success = False
	items = None
	perPage = settings.ITEMS_PER_PAGE
	page = int(request.GET.get("page", 1))
	category = request.GET.get("category", None)
	ordered = {}
	try:
		
		items = Item.objects.filter(auction=currentAuction).order_by(order)
		items = items[perPage*(page-1):(perPage*page)]
		logger.error(items)


		categories = Category.objects.filter(itemCategory__auction=currentAuction).distinct().order_by("order_number")
		
		for item in items:
			
			if item.category.order_number not in ordered:
				ordered[item.category.order_number]= []
				ordered[item.category.order_number].append(item)
				#ordered[item.category.order_number]["category"].append(item.category)
			else:
				ordered[item.category.order_number].append(item)
			'''
		i = 0
		for category in categories:
			objs = Item.objects.filter(auction = currentAuction, category = category).order_by(order)
			
			
			ordered[i]= {}
			ordered[i]["items"] = []
			ordered[i]["items"].append(objs)
			ordered[i]["category"] = category
			i = i+1
		'''

		logger.error(ordered)
			
		
 
	except Exception as e:
		logger.error("Error in catalogByCategory(): %s" % e)

	return render_to_response("catalogByCategory.html", {"sort":"lot_id", "category":category,"categories":categories,"total":total,"ordered":ordered, "auctionId":currentAuction.id, "bids": bidDict, "msg":msg, "number":page, "loggedIn":request.user.is_authenticated(), "success":success}, context_instance=RequestContext(request))


def catalog(request, msg= None):
	
	data = {}
	now =  date.today()
	currentAuction = getCurrentAuction()
	total = 0
	perPage = settings.ITEMS_PER_PAGE
	categories = None

	page = int(request.GET.get("page", 1))
	category = request.GET.get("category", None)
	order = request.GET.get("sort", 'lot_id')
	sortGet= order

	template = "catalog.html"

	logger.error
	if order == "nameAsc":
		order = "name"

	elif order == "nameDesc":
		order = "-name"

	elif order == "artistAsc":
		order = "artist"

	elif order == "artistDesc":
		order = "-artist"
	else:
		order = "lot_id"
		sortGet = "lot_id"
		return catalogByCategory(request, order)


	if not currentAuction:
		return redirect("noAuction")

	success = False
	if request.GET.get("success"):
		success = True

	currentAuctionId = currentAuction.id
	try:
		#if after close but in 2nd chance
		if isSecondChance() or isBetweenSegments():
			
			#only allow winners to bid (so only add on to won shipments)
			bids = Bid.objects.filter(user=request.user, item__auction=currentAuction, winner=True)
			if len(bids) < 1:
				return redirect("noAuction")
			
			if isBetweenSegments():
				return render_to_response('inBetween.html', data, context_instance=RequestContext(request))	
			return redirect("flatFeeCatalog")
	except Exception as e:
		logger.error("error in catalog")
		logger.error(e)
		
	bidDict = {}
	
	try:
		items = None
		categories = Category.objects.filter(itemCategory__auction=currentAuction).distinct()
		
		if category:	
			if int(category) not in categories.values_list("id",flat=True):
				items = Item.objects.filter(auction = currentAuction).order_by(order)
			else:
				items = Item.objects.filter(auction = currentAuction, category = category).order_by(order)
		else:
			items = Item.objects.filter(auction = currentAuction).order_by(order)
		
		total = math.ceil(float(len(items))/perPage)
		bids = []

		
		if page < 1 or page > total:
			return redirect("profile")

		#logger.error("%s : %s" % (perPage*(page-1), (perPage*page)))
		items = items[perPage*(page-1):(perPage*page)]
		if(request.user.is_authenticated()):
			bids = Bid.objects.filter(user = request.user, item__auction = currentAuctionId)
			
		for bid in bids:
			bidDict[str(bid.item.id)] = str(bid.amount)

		if category:
			category = int(category)	
		
	except Exception as e:
		logger.error("error in catalog")
		logger.error(e)
		return redirect("catalog")
	return render_to_response(template, {"sort":sortGet, "category":category,"categories":categories,"total":total,"catItems":items, "auctionId":currentAuctionId, "bids": bidDict, "msg":msg, "number":page, "loggedIn":request.user.is_authenticated(), "success":success}, context_instance=RequestContext(request))


@login_required
def submitBid(request):
	if(request.user.is_authenticated()):
		auction = getCurrentAuction()
		currentAuctionId = auction.id
		now = date.today()
		data = request.POST
		bidAmount = data.get("bidAmount")
		try:
			addresses = Address.objects.filter(user=request.user)
			profile  = UserProfile.objects.get(user=request.user)
			
			if len(addresses) < 1:
				return HttpResponse(json.dumps({"success":False, "msg":"You must have an address on file to bid."}), content_type="application/json")	

			if not profile.verified:
				return HttpResponse(json.dumps({"success":False, "msg":"You must verify your email address before you can bid."}), content_type="application/json")	

			if profile.deadbeat:
				return HttpResponse(json.dumps({"success":False, "msg":"There is a problem with your account.  Please contact us if you'd like to bid."}), content_type="application/json")	

			if profile.quiet:
				return HttpResponse(json.dumps({"success":False, "msg":"You're set to not receive any contact from us.  To bid please go to your settings and uncheck 'Hold all Contact' "}), content_type="application/json")	

				
			itemId = data.get("itemId")

			item = Item.objects.get(id = itemId)

			if not item.auction == auction:
				logger.error("Item id %s not in auction id %s" % (item.id, auction.id))
				return HttpResponse(json.dumps({"success":False, "msg":"Illegal action."}), content_type="application/json")	


			if isSecondChance():
				bidAmount = item.min_bid
				bids = Bid.objects.filter(user=request.user, item__auction=currentAuctionId, winner=True)
				if len(bids) < 1:
					return HttpResponse(json.dumps({"success":False, "msg":"This auction is now closed."}), content_type="application/json")	
			if isBetweenSegments():
				return HttpResponse(json.dumps({"success":False, "msg":"This auction isn't open."}), content_type="application/json")	

			
			if Decimal(bidAmount) < item.min_bid:
				return HttpResponse(json.dumps({"success":False, "msg":"You must meet the minimum bid."}), content_type="application/json")	

			instances = Bid.objects.filter(user=request.user, item_id=itemId)
			if len(instances) < 1:
				bidObj = Bid.objects.create(amount=bidAmount, user=request.user, date=datetime.now(), item_id = itemId)
				if isSecondChance():
					bidObj.winner = True
					bidObj.save()
			else:
				instance = instances[0]	
				instance.amount = bidAmount
				if isSecondChance():
					instance.winner = True
				instance.save()
		
		except Exception as e:
			logger.error("error submitting bid")
			logger.error(e)
			return HttpResponse(json.dumps({"success":False, "msg":"Illegal action."}), content_type="application/json")	


	return HttpResponse(json.dumps({"success":True}), content_type="application/json")	
	
@login_required
def deleteBid(request):
	if(request.user.is_authenticated()):
		data = request.POST
		itemId = data.get("itemId")
		instance = Bid.objects.get(user=request.user, item_id=itemId)
		instance.delete()

	logger.error("path : %s" % request.META.get('PATH_INFO'))
	if isSecondChance():
		return redirect("bids")
	if(request.META.get('PATH_INFO') == "/audio/catalog/deleteBid"):
		return redirect("catalog")

		
	else:
		return redirect("bids")
	
def itemInfo(request, itemId):
	data = {}
	items = Item.objects.filter(pk=itemId)
	if len(items) < 1:
		data["errorMsg"] = "That is not a valid item."
	else:
		data["item"]  = items[0]
	return render_to_response('itemInfo.html', {"data":data}, context_instance=RequestContext(request))


@login_required
def showItem(request, auctionId, lotId):
	if request.method == 'POST':
		form = BidSubmitForm(request.POST)

		if form.is_valid():
			bid = form.save()	
	else:
		form = BidSubmitForm()
	return render_to_response('item.html', {"form":form, "auctionId":auctionId}, context_instance=RequestContext(request))
