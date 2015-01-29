from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect

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

import logging
import json, math



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
	if request.method == "POST":
		if(request.user.is_authenticated()):

			try:
				addresses = Address.objects.filter(user=request.user)
		
				if len(addresses) < 1:
					return render_to_response('item.html', {"form":form, "success": False, "msg":"You must have an address on file to bid."}, context_instance=RequestContext(request))					
			
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
		if isSecondChance():
			bids = Bid.objects.filter(user=request.user, item__auction=currentAuction, winner=True)
			if len(bids) < 1:
				return redirect("noAuction")
			return redirect("flatFeeCatalog")

		if currentAuction == None:
			return render_to_response('noAuction.html', data, context_instance=RequestContext(request))

		form = BidSubmitForm(auctionId = currentAuction.id)

	return render_to_response('item.html', {"form":form}, context_instance=RequestContext(request))
		
	
def contact_info(request):
	if request.method == 'POST':
		try:
			instance = Address.objects.get(user=request.user)
			form = ContactForm(request.POST, instance = instance)
		except:
			form = ContactForm(request.POST)

		
		if form.is_valid():
			contact = form.save(commit=False)
			contact.user = request.user
			contact.save()
			return render_to_response('contact.html', {"form":form, "success": True}, context_instance=RequestContext(request))
		else:
			return render_to_response('contact.html', {"form":form}, context_instance=RequestContext(request))

	try:
		address = Address.objects.get(user=request.user)
	except:
		address = Address()
	form = ContactForm(instance=address)
	return render_to_response('contact.html', {"form":form}, context_instance=RequestContext(request))


def register(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            nu = authenticate(username=request.POST['username'],
                                    password=request.POST['password1'])
            login(request, nu)
           
            return HttpResponseRedirect("../profile")
    else:
        form = UserCreateForm()
    return render(request, "registration/register.html", {
        'form': form,
    })


def bids(request):
	if(request.user.is_authenticated()):
		currentAuction = getCurrentAuction()
		
		if not currentAuction:
			return redirect('noAuction')

		currentAuctionId = currentAuction.id
		bids = Bid.objects.filter(item__auction = currentAuctionId, user= request.user)
		success = False
		if request.GET.get("success"):
			success = True
		invoices = Invoice.objects.filter(user = request.user, auction = currentAuction.id)
		invoice = None
		if len(invoices) > 0:
			invoice = invoices[0]
			
		if isSecondChance():
			if invoice == None or invoice.second_chance_invoice_amount == None:
				bids = Bid.objects.filter(item__auction = currentAuctionId, date__gt = currentAuction.end_date)
				
				return render_to_response('flatBids.html', {"success":success, "bids":bids, "endAuctionOption":True, "auctionId":currentAuctionId}, context_instance=RequestContext(request))
			else:
				#They've already ended their auction.  Summary?
				return redirect("auctionSummaries")

		else:
			return render_to_response('bids.html', {"success":success,"bids":bids}, context_instance=RequestContext(request))
	else:
		return redirect("profile")

def auctionSummaries(request):
	data = {}
	if(request.user.is_authenticated()):
		data["auctions"] = getWonAuctions(request.user.id)
		return render_to_response('auctionSummaries.html', {"data":data}, context_instance=RequestContext(request))
	else:
		return redirect("profile")


def auctionSummary(request, auctionId):
	data={}
	if(request.user.is_authenticated()):
		auctions = Auction.objects.filter(id=auctionId)
		
		if len(auctions) < 1:
			return redirect("catalog")
		
		currentAuction = auctions[0]
		
		#if still in auction
		#if blind

		if not currentAuction.blind_locked:
			return redirect("catalog")

		data["auction"] = currentAuction
		data["bids"] = Bid.objects.filter(user = request.user, item__auction = currentAuction, winner = True)

		return render_to_response('endingBids.html', {"data":data}, context_instance=RequestContext(request))
	
	return redirect("catalog")




def profile(request):
	data = {}
	if request.user.is_authenticated():
		addresses = Address.objects.filter(user=request.user)
		if len(addresses) < 1:
			data["addressMsg"]=True
	return render_to_response('profile.html', {"data":data}, context_instance=RequestContext(request))

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



def flatFeeCatalog(request):
	items = None
	if request.user.is_authenticated():
		if not isSecondChance():
			return redirect("catalog")

		auction = getCurrentAuction()
		try:

			invoices = Invoice.objects.filter(user = request.user, auction = auction)
			invoice = None
		
			if len(invoices) > 0:
				invoice = invoices[0]
				if invoice.second_chance_invoice_amount > 0:
					return redirect("auctionSummaries")

			items = Item.objects.filter(bid=None)
		except Exception as e:
			logger.error("error in catalog")
			logger.error(e)
		
		return render_to_response('flatCatalog.html', {"catItems":items, "auctionId":auction.id}, context_instance=RequestContext(request))
	return redirect("profile")


def noAuction(request):
	data = {}
	currentAuction = getCurrentAuction()

	if currentAuction and not isSecondChance():
		return redirect("catalog")
	return render_to_response('noAuction.html', data, context_instance=RequestContext(request))

def catalog(request, msg= None):
	
	data = {}
	now =  date.today()
	currentAuction = getCurrentAuction()
	total = 0
	perPage = 3
	categories = None

	page = int(request.GET.get("page", 1))
	category = request.GET.get("category", None)
	order = request.GET.get("sort", 'lot_id')
	sortGet= order


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



	if not currentAuction:
		return redirect("noAuction")

	success = False
	if request.GET.get("success"):
		success = True

	currentAuctionId = currentAuction.id
	try:
		#if after close but in 2nd chance
		if isSecondChance():
		
			#only allow winners to bid (so only add on to won shipments)
			bids = Bid.objects.filter(user=request.user, item__auction=currentAuction, winner=True)
			if len(bids) < 1:
				return redirect("noAuction")
			return redirect("flatFeeCatalog")
	except Exception as e:
		logger.error("error in catalog")
		logger.error(e)
		
	bidDict = {}
	
	try:
		items = None
		categories = Category.objects.filter(item__auction=currentAuction).distinct()

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
	return render_to_response('catalog.html', {"sort":sortGet, "category":category,"categories":categories,"total":total,"catItems":items, "auctionId":currentAuctionId, "bids": bidDict, "msg":msg, "number":page, "loggedIn":request.user.is_authenticated(), "success":success}, context_instance=RequestContext(request))



def submitBid(request):
	if(request.user.is_authenticated()):
		auction = getCurrentAuction()
		currentAuctionId = auction.id
		now = date.today()
		data = request.POST
		bidAmount = data.get("bidAmount")
		
		addresses = Address.objects.filter(user=request.user)
		
		if len(addresses) < 1:
			return HttpResponse(json.dumps({"success":False, "msg":"You must have an address on file to bid."}), content_type="application/json")	

		itemId = data.get("itemId")
		item = Item.objects.get(id = itemId)

		if isSecondChance():
			bidAmount = item.min_bid
			bids = Bid.objects.filter(user=request.user, item__auction=currentAuctionId, winner=True)
			if len(bids) < 1:
				return HttpResponse(json.dumps({"success":False, "msg":"This auction is now closed."}), content_type="application/json")	

		
		if Decimal(bidAmount) < item.min_bid:
			return HttpResponse(json.dumps({"success":False, "msg":"You must meet the minimum bid."}), content_type="application/json")	

		try:
			instance = Bid.objects.get(user=request.user, item_id=itemId)
			instance.amount = bidAmount
			instance.save()
		except:	
			if(bidAmount == None or bidAmount == ""):
				logger.error("no bid")
			else:
				Bid.objects.create(amount=bidAmount, user=request.user, date=datetime.now(), item_id = itemId)

	return HttpResponse(json.dumps({"success":True}), content_type="application/json")	
	

def deleteBid(request):
	if(request.user.is_authenticated()):
		data = request.POST
		itemId = data.get("itemId")
		instance = Bid.objects.get(user=request.user, item_id=itemId)
		instance.delete()

	if(request.META.get('PATH_INFO') == "/audio/catalog/deleteBid"):
		return redirect("catalog")
	else:
		return redirect("bids")
		

def showItem(request, auctionId, lotId):
	if request.method == 'POST':
		form = BidSubmitForm(request.POST)

		if form.is_valid():
			bid = form.save()	
	else:
		form = BidSubmitForm()
	return render_to_response('item.html', {"form":form, "auctionId":"1"}, context_instance=RequestContext(request))
