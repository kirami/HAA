from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.core.mail import send_mail

from audio.forms import ContactForm, BidSubmitForm

from audio.models import Address, Item, Bid, Auction

from datetime import datetime, date  

import logging
import json



# Get an instance of a logger
logger = logging.getLogger(__name__)

def test(request):
	data = {}
	send_mail('Subject here', 'Here is the message.', 'from@example.com',
    ['kirajmd@gmail.com'], fail_silently=False)
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

def simpleForm(request):
	form = ''
	if request.method == "POST":
		if(request.user.is_authenticated()):
			currentAuctionId = 1
			auction = Auction.objects.get(id = currentAuctionId)
			now = date.today()
			data = request.POST
			bidAmount = data.get("bidAmount")

			if isSecondChance():
				bidAmount = auction.flat_bid_amount

			itemId = Item.objects.get(log_id = data.get("lotId"))
			try:
				instance = Bid.objects.get(user=request.user, item_id=itemId)
				instance.amount = bidAmount
				instance.save()
			except:	
				if(bidAmount == None or bidAmount == ""):
					logger.error("no bid")
				else:
					#todo get auctionId from...db?
					Bid.objects.create(amount=bidAmount, user=request.user, date=datetime.now(), auction_id=currentAuctionId, item_id = itemId, second_chance_bid = isSecondChance())
	else:
		form = BidSubmitForm()

	return render_to_response('item.html', {"form":form}, context_instance=RequestContext(request))
	#logger.error(request.META.get('PATH_INFO'))			
	
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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("../profile")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })


def bids(request):
	currentAuctionId = 1
	bids = Bid.objects.filter(auction_id = currentAuctionId)

	if isSecondChance():
		bids = Bid.objects.filter(auction_id = currentAuctionId, second_chance_bid = isSecondChance())
		return render_to_response('flatBids.html', {"bids":bids}, context_instance=RequestContext(request))
	else:
		return render_to_response('bids.html', {"bids":bids}, context_instance=RequestContext(request))




def profile(request):

	return render_to_response('profile.html', {}, context_instance=RequestContext(request))


def flatFeeCatalog(request):
	try:
		items = Item.objects.filter(bid=None)
	except Exception as e:
		logger.error("error in catalog")
		logger.error(e)
	
	return render_to_response('flatCatalog.html', {"catItems":items, "auctionId":"1"}, context_instance=RequestContext(request))

def isSecondChance():
	now =  date.today()
	currentAuctionId = 1
	auction = Auction.objects.get(id = currentAuctionId)
	if auction.end_date < now and auction.second_chance_end_date > now:
		return True
	return False

def catalog(request):
	
	now =  date.today()
	logger.error(now)
	#TODO get real data
	currentAuctionId = 1
	try:
		#if after close but in 2nd chance
		if isSecondChance():
			return redirect("flatFeeCatalog")
	except Exception as e:
		logger.error("error in catalog")
		logger.error(e)
		

	items = ""
	try:
		items = Item.objects.all()	
		bids = Bid.objects.filter(auction_id = currentAuctionId)
		bidDict = {}
		for bid in bids:
			bidDict[str(bid.item.id)] = str(bid.amount)

		logger.error(bidDict.get("1"))
		
	except Exception as e:
		logger.error("error in catalog")
		logger.error(e)
	return render_to_response('catalog.html', {"catItems":items, "auctionId":"1", "bids": bidDict}, context_instance=RequestContext(request))


def submitBid(request):
	if(request.user.is_authenticated()):
		currentAuctionId = 1
		auction = Auction.objects.get(id = currentAuctionId)
		now = date.today()
		data = request.POST
		bidAmount = data.get("bidAmount")
		

		if isSecondChance():
			bidAmount = auction.flat_bid_amount

		itemId = data.get("itemId")
		logger.error("request:")
		logger.error(request)
		try:
			instance = Bid.objects.get(user=request.user, item_id=itemId)
			instance.amount = bidAmount
			instance.save()
		except:	
			if(bidAmount == None or bidAmount == ""):
				logger.error("no bid")
			else:
				#todo get auctionId from...db?
				Bid.objects.create(amount=bidAmount, user=request.user, date=datetime.now(), auction_id=currentAuctionId, item_id = itemId, second_chance_bid = isSecondChance())

	#logger.error(request.META.get('PATH_INFO'))			
	if(request.META.get('PATH_INFO') == "/audio/catalog/submitBid"):
		return redirect("catalog")
	else:
		return redirect("bids")

def deleteBid(request):
	if(request.user.is_authenticated()):
		data = request.POST
		itemId = data.get("itemId")
		instance = Bid.objects.get(user=request.user, item_id=itemId)
		instance.delete()

	return redirect("bids")
		

def showItem(request, auctionId, lotId):
	"""
    form = ""
    logger.error("HELLO")
    if request.method == 'POST':
    	
    	form = BidSubmitForm(request.POST)
    	if form.is_valid():
    		bid = form.save()
    		return render_to_response('item.html', {"form":form, "success": True}, context_instance=RequestContext(request))
    	else:
			return render_to_response('item.html', {"form":form, "success": True}, context_instance=RequestContext(request))
	"""
	if request.method == 'POST':
		form = BidSubmitForm(request.POST)

		if form.is_valid():
			bid = form.save()	
	else:
		form = BidSubmitForm()
	return render_to_response('item.html', {"form":form, "auctionId":"1"}, context_instance=RequestContext(request))
