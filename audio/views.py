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

from audio.models import Address, Item, Bid, Auction, UserProfile, Invoice, Category, ItemType

from datetime import datetime, date  
from django.conf import settings
from audio.utils import *
from audio.mail import *

import logging
import json, math, string, random, collections


from django.views.generic import TemplateView
from django.template import TemplateDoesNotExist
from django.http import Http404




# Get an instance of a logger
logger = logging.getLogger(__name__)


class StaticView(TemplateView):
    def get(self, request, page, *args, **kwargs):
        
        self.template_name = "site/" +page
        #logger.info("page %s" % page)
        response = super(StaticView, self).get(request, *args, **kwargs)
        try:
            return response.render()
        except TemplateDoesNotExist:
            self.template_name = page
            response = super(StaticView, self).get(request, *args, **kwargs)
            try:
            	return response.render()
            except TemplateDoesNotExist:
            	raise Http404()


def test(request):
	data = {}
	return render_to_response('contact.html', {"data":data}, context_instance=RequestContext(request))



def audio(request):
	return redirect("index")

def index(request):
	t = loader.get_template('site/index.html')
	c = RequestContext(request, {'foo': 'bar'})
	return HttpResponse(t.render(c), content_type="text/html")


@login_required
def simpleForm(request):
	form = None
	data = {}
	now = date.today()
	currentAuction = getCurrentAuction()
	data["auction"] = currentAuction
	if(request.user.is_authenticated()):
		
		if request.method == "POST":
			try:
				up  = UserProfile.objects.get(user=request.user)
			
				if not up.shipping_address or not up.billing_address:
					logger.error("simpleForm: tried to bid without address")
					return render_to_response('simpleForm.html', {"form":form, "success": False, "msg":"You must have an address on file to bid."}, context_instance=RequestContext(request))					
				
				if up.deadbeat:
					logger.error("simpleForm: tried to bid while db")
					return render_to_response('simpleForm.html', {"form":form, "success": False, "msg":"There is a problem with your account.  Please contact us if you'd like to bid"}, context_instance=RequestContext(request))					
				
				if up.quiet:
					logger.error("simpleForm: tried to bid while quiet")
					return HttpResponse(json.dumps({"success":False, "msg":"You're set to not receive any contact from us.  To bid please go to your profile and uncheck 'I want no contact' "}), content_type="application/json")	


				form = BidSubmitForm(currentAuction.id, request.POST)
			except Exception as e:
				logger.error("simpleForm exception: %s" % e)
				return render_to_response('simpleForm.html', {"form":form, "success": False}, context_instance=RequestContext(request))
			
			if form.is_valid():
				bid = form.save(commit=False)
				bid.user = request.user
				bid.date = datetime.now()
				try:
					bid.save()
				except Exception as e:
					logger.error("simpleForm: dupe bid %s" % e)
					#if e[0] == 1062:
						#logger.error("simpleForm: dupe bid")
					return render_to_response('simpleForm.html', {"form":form, "success": False, "msg":"You've already bid on this item.  Please go to your account to edit/delete"}, context_instance=RequestContext(request))					
				return render_to_response('simpleForm.html', {"form":form, "success": True}, context_instance=RequestContext(request))
			else:
				logger.error("simpleForm: form not valid")
				return render_to_response('simpleForm.html', {"form":form, "success":False, "msg":"We could not save your bid."}, context_instance=RequestContext(request))

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
	return render_to_response('simpleForm.html', {"form":form, "data": data}, context_instance=RequestContext(request))


@login_required
def accountSettings(request):
	data = {}
	up = UserProfile.objects.get(user = request.user)
	if request.method == "POST":
		try:
			quiet = request.POST.get("quietBox", None)
			noPC = request.POST.get("noPCBox", None)
			snailMail = request.POST.get("snailMailBox", None)

			up.quiet = True if quiet else False
			up.pdf_list = True if noPC else False
			up.email_only = False if snailMail else True

			up.save()
			data["success"] = True
		except:
			data["error"] = True
			return render_to_response('settings.html', {"data":data}, context_instance=RequestContext(request))

	data["profile"] = up
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
	emailData["url"] = settings.EMAIL_URL+"accounts/confirm/" + str(p.confirmation_code) + "/" + user.username
	emailData["user"]=user
	msg = getEmailMessage(user.email,"Welcome to Hawthorn's Antique Audio!",{"data":emailData}, "verifyEmail")
	sendEmail(msg)


def verifyEmail(request):
	if(request.user.is_authenticated()):
		send_registration_confirmation(request.user)
		data = {}
		data["user"] = request.user
		data["resent"]=True
		#logger.info("resent")
		return render_to_response('verified.html', {"data":data}, context_instance=RequestContext(request))
	else:
		return redirect("profile")	

def resetPassword(request):
	
	data = {}
	if request.POST:
		try:
			username = request.POST.get("username")
			users = User.objects.filter(username = username)
			if len(users) < 1:
				data["errorMsg"]="That username hasn't been registered with us."
				logger.error("tried to reset unregistered account: %s" % username)
				return render_to_response('resetPassword.html', {"data":data}, context_instance=RequestContext(request))	
			user = users[0]
			password = User.objects.make_random_password()
			user.set_password(password)
			user.save()
			#logger.info("user: %s" %user.email)
			emailData={}
			emailData["user"] = user
			emailData["password"] = password	
			msg = getEmailMessage(user.email,"We received a request to reset your password",{"data":emailData}, "resetPassword")
			sendEmail(msg)
		except Exception as e:
			logger.error("Error reseting password: %s" % e)
			data["errorMsg"]="Something went wrong.  Please contact us."
			return render_to_response('resetPassword.html', {"data":data}, context_instance=RequestContext(request))	
		
		data["success"]=True
		return render_to_response('resetPassword.html', {"data":data}, context_instance=RequestContext(request))	
	
	return render_to_response('resetPassword.html', {"data":data}, context_instance=RequestContext(request))					

def confirm(request, confirmation_code, username):
	data = {}
	try:
		users = UserProfile.objects.filter(user__username=username)
		user = User.objects.get(username = username)
		profile = None
		
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
	

	except Exception as e:
		logger.error("error in confirm %s" % e)
		data["errorMsg"] = "We could not verify your account, please contact us."
		return render_to_response('verified.html', {"data":data}, context_instance=RequestContext(request))
	return render_to_response('verified.html', {"data":data}, context_instance=RequestContext(request))

@login_required
def bids(request):
	data = {}
	data["bidPage"] = True
	if(request.user.is_authenticated()):
		currentAuction = getCurrentAuction()
		
		if not currentAuction:
			return redirect('noAuction')

		currentAuctionId = currentAuction.id
		bids = Bid.objects.filter(item__auction = currentAuctionId, user= request.user).order_by("item__lot_id")
		#logger.error("bids: %s" % bids)
		#logger.error("user: %s" % request.user)

		success = False
		if request.GET.get("success"):
			success = True
		invoices = Invoice.objects.filter(user = request.user, auction = currentAuction.id)
		invoice = None
		if len(invoices) > 0:
			invoice = invoices[0]
			
		if isBetweenSegments():
			return redirect('noAuction')

		if isSecondChance():
			data["flat"] = True
			if invoice == None or invoice.second_chance_invoice_amount == 0:
				bids = Bid.objects.filter(item__auction = currentAuctionId, date__gt = currentAuction.end_date, user=request.user)
				
				return render_to_response('flatBids.html', { "loggedIn":True, "data":data,"success":success, "bids":bids, "endAuctionOption":True, "auctionId":currentAuctionId, "total":1 ,"number":1 }, context_instance=RequestContext(request))
			else:
				#They've already ended their auction.  Summary?
				return redirect('noAuction')
				#return render_to_response('flatBids.html', {"loggedIn":True,"data":data,"success":success, "bids":bids, "ended":True, "auctionId":currentAuctionId, "total":1 ,"number":1 }, context_instance=RequestContext(request))
			

		else:
			return render_to_response('bids.html', {"loggedIn":True,"data":data,"success":success,"bids":bids,"total":1 ,"number":1 }, context_instance=RequestContext(request))
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
				return render(request, "userInfo.html", {'form': form, "success":True})
		else:
			form = UserForm(instance=request.user)
		return render(request, "userInfo.html", {'form': form,})
	else:
		return redirect("profile")


@login_required
def flatFeeCatalog(request):
	items = None
	auction = getCurrentAuction()
	data = {}
	data["auction"]=auction
	data["flat"] = True
	
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
					return redirect("noAuction")
				
			bids = Bid.objects.filter(user=request.user, item__auction=auction, winner=True)
			if len(bids) < 1:	
				return redirect("noAuction")
			
			if isBetweenSegments():
				return render_to_response('inBetween.html', data, context_instance=RequestContext(request))	

			items = getNoBidItems(auction.id)
		except Exception as e:
			logger.error("error in catalog")
			logger.error(e)
		
		return render_to_response('flatCatalog.html', {"loggedIn": True,"data":data,"catItems":items, "auctionId":auction.id, "success":success, "total":1 ,"number":1 , "flat":True}, context_instance=RequestContext(request))
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
						invoices = Invoice.objects.filter(user = request.user, auction = currentAuction)
						invoice = None
						#if user ended their auction and got an invoice
						if len(invoices) > 0:
							invoice = invoices[0]
							if invoice.second_chance_invoice_amount > 0:
								return render_to_response('noAuction.html', data, context_instance=RequestContext(request))
						return redirect("flatFeeCatalog")
				else:
					return redirect("catalog")
			except:
				return render_to_response('noAuction.html', data, context_instance=RequestContext(request))
		elif isSecondChance() or isBetweenSegments():
			return render_to_response('noAuction.html', data, context_instance=RequestContext(request))
		
		else: 
			return redirect("catalog")
	return render_to_response('noAuction.html', data, context_instance=RequestContext(request))

def catalogByCategory(request, order, auctionId = None):
	data = {}
	currentAuction = getCurrentAuction()

	if request.user and request.user.is_staff and auctionId:
		currentAuction = Auction.objects.get(pk = auctionId)
	
	#if not request.user or (not request.user.is_staff and auctionId):
	#	return redirect("catalog")
	
	data["auction"]=currentAuction
	total = 1
	bidDict = {}
	msg = ""
	success = False
	items = None
	perPage =  settings.ITEMS_PER_PAGE
	page = 1
	jumpLotId = request.GET.get("jump", None)
	try:
		page = int(request.GET.get("page", 1))
	except:
		logger.error("bad page")

	category = request.GET.get("category", None)
	ordered = {}
	categories = None
	itemType = None
	firstLibraryKey = None
	sortGet = "lotAsc"
	
	if order == "-lot_id":
		sortGet = "lotDesc"
	else:
		sortGet = "lotAsc"
		
	
	try:
		
		
		items = Item.objects.filter(auction=currentAuction).order_by(order)

		if jumpLotId:

			page = math.floor(int(jumpLotId) / 20) + 1
			#logger.info("page %s" % page)

		total = math.ceil(float(len(items))/perPage)
		
		if page > total:
			page = 1

		items = items[perPage*(page-1):(perPage*page)]
		#logger.error(items)

		'''if order == "-lot_id":
			catSort = "-order_number"
		else:
			catSort = "order_number"
		'''
		catSort = "order_number"

		if itemType:
			itemType = ItemType.objects.get(name="Record")
			categories = Category.objects.filter(itemCategory__auction=currentAuction, itemCategory__item_type = itemType).distinct().order_by("order_number")
		
		else: 
			categories = Category.objects.filter(itemCategory__auction=currentAuction).distinct().order_by(catSort)

			#logger.error("categories %s" % categories)

		for item in items:

			if item.item_type.name != "Record" and not firstLibraryKey:
				firstLibraryKey = item.category.order_number

			if item.category.order_number not in ordered:
				#logger.error("adding ordered: %s" % item.category.order_number)
				ordered[int(item.category.order_number)]= []
				ordered[int(item.category.order_number)].append(item)
				#ordered[item.category.order_number]["category"].append(item.category)
			else:
				ordered[int(item.category.order_number)].append(item)

		#logger.error("after loop %s" % ordered)
		
		
		
		od = collections.OrderedDict(sorted(ordered.items()))
		#logger.error("after first sort %s" % od)
		if order == "-lot_id":
			items = od.items()  # list(od.items()) in Python3
			items.reverse()
			od = collections.OrderedDict(items)
			#od = items
			#logger.error("after reverse %s" % od)



		
		ordered = od

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
		
		#logger.error(ordered)
		bids = []
		if(request.user.is_authenticated()):
			bids = Bid.objects.filter(user = request.user, item__auction = currentAuction.id)
		
		for bid in bids:
			bidDict[str(bid.item.id)] = str(bid.amount)	

		if request.GET.get("success"):
			success = True

	except Exception as e:
		logger.error("Error in catalogByCategory(): %s" % e)

	return render_to_response("catalogByCategory.html", {"data":data,"sort":sortGet, "category":category,"categories":categories,"total":total,"ordered":ordered, "auctionId":currentAuction.id, "bids": bidDict,  "number":page, "loggedIn":request.user.is_authenticated(), "success":success, "firstLibraryKey": firstLibraryKey}, context_instance=RequestContext(request))


def catalog(request, auctionId = None):
	msg = ""
	data = {}
	now =  date.today()
	
	currentAuction = getCurrentAuction()

	if request.user and request.user.is_staff and auctionId:
		currentAuction = Auction.objects.get(pk = auctionId)
	#why???
	#if not request.user or (not request.user.is_staff and auctionId):
	#	return redirect("catalog")

	
	data["auction"]=currentAuction
	total = 0
	perPage = settings.ITEMS_PER_PAGE
	categories = None
	page = 1
	try:
		page = int(request.GET.get("page", 1))
	except:
		logger.error("bad page")

	category = request.GET.get("category", None)
	order = request.GET.get("sort", 'lot_id')
	sortGet= order
	currentAuctionId = None

	if not currentAuction:
		return redirect("noAuction")

		currentAuctionId = currentAuction.id
	try:
		#logger.info("1")
		#if after close but in 2nd chance
		if isSecondChance() or isBetweenSegments():
			logger.info("2")
			
			#only allow winners to bid (so only add on to won shipments)
			logger.info("user: %s" % request.user)
			if request.user.is_authenticated():
				bids = Bid.objects.filter(user=request.user, item__auction=currentAuction, winner=True)
				logger.info("bids")
				if len(bids) < 1:
					logger.info("3")
					return redirect("noAuction")
			else:	
				return redirect("noAuction")
			
			if isBetweenSegments():
				logger.info("4")
				return render_to_response('inBetween.html', data, context_instance=RequestContext(request))	
			return redirect("flatFeeCatalog")
	except Exception as e:
		logger.error("error in catalog")
		logger.error(e)

	template = "catalog.html"

	
	if order == "nameAsc":
		order = "name"

	elif order == "nameDesc":
		order = "-name"

	elif order == "artistAsc":
		order = "artist"

	elif order == "artistDesc":
		order = "-artist"
	elif order == "lotDesc":
		order = "-lot_id"
		return catalogByCategory(request, order, auctionId)
	elif not category:
		order = "lot_id"
		sortGet = "lot_id"
		return catalogByCategory(request, order, auctionId)


	success = False
	if request.GET.get("success"):
		success = True


		
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
		#logger.error("cat total: %s" % total)

		
		if page < 1 or page > total:
			return redirect("profile")

		#logger.error("%s : %s" % (perPage*(page-1), (perPage*page)))
		items = items[perPage*(page-1):(perPage*page)]
		if(request.user.is_authenticated()):
			bids = Bid.objects.filter(user = request.user, item__auction = currentAuction.id)
			
		for bid in bids:
			bidDict[str(bid.item.id)] = str(bid.amount)
		#logger.error("bid dict: %s" % bidDict)

		if category:
			category = Category.objects.get(pk=category)	
		
	except Exception as e:
		logger.error("error in catalog")
		logger.error(e)
		return redirect("catalog")
	return render_to_response(template, {"data":data, "sort":sortGet, "category":category,"categories":categories,"total":total,"catItems":items, "auctionId":currentAuctionId, "bids": bidDict, "msg":msg, "number":page, "loggedIn":request.user.is_authenticated(), "success":success}, context_instance=RequestContext(request))


@login_required
def submitBid(request):
	if(request.user.is_authenticated()):
		auction = getCurrentAuction()
		currentAuctionId = auction.id
		now = date.today()
		data = request.POST
		bidAmount = data.get("bidAmount")

		if not bidAmount:
			return HttpResponse(json.dumps({"success":False, "msg":"You must enter a bid amount."}), content_type="application/json")	

		try:
			profile  = UserProfile.objects.get(user=request.user)
			
			if not profile.shipping_address:
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

	#logger.info("path : %s" % request.META.get('PATH_INFO'))
	
	if data.get("bidPage", False):
		return redirect("bids") 

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

"""
@login_required
def showItem(request, auctionId, lotId):
	if request.method == 'POST':
		form = BidSubmitForm(request.POST)

		if form.is_valid():
			bid = form.save()	
	else:
		form = BidSubmitForm()
	return render_to_response('item.html', {"form":form, "auctionId":auctionId}, context_instance=RequestContext(request))
"""
