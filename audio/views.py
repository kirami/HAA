from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect

from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import login

from django.template import RequestContext, loader
from django.core.mail import send_mail

from audio.forms import ContactForm, BidSubmitForm, UserCreateForm, UserForm

from audio.models import Address, Item, Bid, Auction, UserProfile, Invoice

from datetime import datetime, date  

import logging
import json



# Get an instance of a logger
logger = logging.getLogger(__name__)

def test(request):
	data = {}
	return render_to_response('contact.html', {"data":data}, context_instance=RequestContext(request))


def index(request):
	t = loader.get_template('home.html')
	c = RequestContext(request, {'foo': 'bar'})
	return HttpResponse(t.render(c), content_type="text/html")
'''
def login_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        # Correct password, and the user is marked "active"
        auth.login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect("/account/loggedin/")
    else:
        # Show an error page
        return HttpResponseRedirect("/account/invalid/")
'''

def getCurrentAuction():
	now = date.today()
	# where date is after start date and before second_end date
	auctions = Auction.objects.filter(start_date__lte = now, second_chance_end_date__gte = now)
	if len(auctions) == 1:
		return auctions[0]
	else:
		#TODO throw error
		return None

def simpleForm(request):
	form = None
	data = None
	now = date.today()
	currentAuction = getCurrentAuction()
	if request.method == "POST":
		if(request.user.is_authenticated()):

			try:
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
           
            return HttpResponseRedirect("../profile")
    else:
        form = UserCreateForm()
    return render(request, "registration/register.html", {
        'form': form,
    })


def bids(request):
	if(request.user.is_authenticated()):
		currentAuction = getCurrentAuction()
		currentAuctionId = currentAuction.id
		bids = Bid.objects.filter(item__auction = currentAuctionId, user= request.user)
		invoices = Invoice.objects.filter(user = request.user, auction = currentAuction.id)
		invoice = None
		if len(invoices) > 0:
			invoice = invoices[0]
			
		if isSecondChance():
			if invoice == None or invoice.second_chance_invoice_amount == None:
				bids = Bid.objects.filter(item__auction = currentAuctionId, date__gt = currentAuction.end_date)
				
				return render_to_response('flatBids.html', {"bids":bids, "endAuctionOption":True, "auctionId":currentAuctionId}, context_instance=RequestContext(request))
			else:
				#TODO return error
				index()
		else:
			return render_to_response('bids.html', {"bids":bids}, context_instance=RequestContext(request))
	else:
		index()




def profile(request):
	return render_to_response('profile.html', {}, context_instance=RequestContext(request))

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
	if not isSecondChance():
		return redirect("catalog")

	auction = getCurrentAuction()
	try:

		items = Item.objects.filter(bid=None)
	except Exception as e:
		logger.error("error in catalog")
		logger.error(e)
	
	return render_to_response('flatCatalog.html', {"catItems":items, "auctionId":auction.id}, context_instance=RequestContext(request))

def isSecondChance():
	now =  datetime.now()
	#TODO current auction
	currentAuction = getCurrentAuction()
	currentAuctionId = currentAuction.id
	auction = Auction.objects.get(id = currentAuctionId)
	if auction.end_date < now and auction.second_chance_end_date > now:
		return True
	return False

def catalog(request, msg= None):
	if(request.user.is_authenticated()):
		data = {}
		now =  date.today()
		currentAuction = getCurrentAuction()

		if not currentAuction:
			return render_to_response('noAuction.html', data, context_instance=RequestContext(request))

		currentAuctionId = currentAuction.id
		try:
			#if after close but in 2nd chance
			if isSecondChance():
				return redirect("flatFeeCatalog")
		except Exception as e:
			logger.error("error in catalog")
			logger.error(e)
			
		bidDict = {}
		items = ""
		try:
			items = Item.objects.all()	
			bids = Bid.objects.filter(user = request.user, item__auction = currentAuctionId)
			
			for bid in bids:
				bidDict[str(bid.item.id)] = str(bid.amount)

			#logger.error(bidDict.get("1"))
			
		except Exception as e:
			logger.error("error in catalog")
			logger.error(e)
	return render_to_response('catalog.html', {"catItems":items, "auctionId":currentAuctionId, "bids": bidDict, "msg":msg}, context_instance=RequestContext(request))


def submitBid(request):
	if(request.user.is_authenticated()):
		auction = getCurrentAuction()
		currentAuctionId = auction.id
		now = date.today()
		data = request.POST
		bidAmount = data.get("bidAmount")
		

		

		itemId = data.get("itemId")
		item = Item.objects.get(id = itemId)

		if isSecondChance():
			bidAmount = item.min_bid
		
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
				#todo get auctionId from...db?
				Bid.objects.create(amount=bidAmount, user=request.user, date=datetime.now(), item_id = itemId)

	return HttpResponse(json.dumps({"success":True}), content_type="application/json")	
	'''
	#logger.error(" path: %s" % request.META.get('PATH_INFO'))			
	if(request.META.get('PATH_INFO') == "/audio/catalog/submitBid" ):
		return HttpResponse(json.dumps({"success":True, "location":"You must meet the minimum bid."}), content_type="application/json")	

	else:
		return HttpResponse(json.dumps({"success":True, "msg":"You must meet the minimum bid."}), content_type="application/json")	
	'''

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
