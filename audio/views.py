from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader

from audio.forms import ContactForm, BidSubmitForm

from audio.models import Address, Item, Bid

from datetime import datetime  

import logging
import json



# Get an instance of a logger
logger = logging.getLogger(__name__)

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

	return render_to_response('bids.html', {}, context_instance=RequestContext(request))

def profile(request):

	return render_to_response('profile.html', {}, context_instance=RequestContext(request))


def catalog(request):
	items = ""
	try:
		items = Item.objects.all()	
		bids = Bid.objects.filter(auction_id = 1)
		bidDict = {}
		for bid in bids:
			bidDict[str(bid.item.id)] = str(bid.amount)

		logger.error(bidDict.get("1"))
		
	except Exception as e:
		logger.error("error in catalog")
		logger.error(e)
	return render_to_response('catalog.html', {"catItems":items, "auctionId":"1", "bids": bidDict}, context_instance=RequestContext(request))

'''
def showItem(request, auctionId, lotId):
	item = ""
	logger.error("in catalog")
	try:
		item = Item.objects.get(lot_id=lotId)
		
	except Exception as e:
		logger.error("error in catalog")
		logger.error(e)
	return render_to_response('item.html', {"item":item, "auctionId":"1"}, context_instance=RequestContext(request))
'''

def submitBid(request):
	if(request.user.is_authenticated()):
		data = request.POST
		bidAmount = data.get("bidAmount")
		itemId = data.get("itemId")
		logger.error(data)
		logger.error(itemId)
		if(bidAmount == None or bidAmount == ""):
			logger.error("no bid")
		else:
			#todo get auctionId from...db?
			Bid.objects.create(amount=bidAmount, user=request.user, date=datetime.now(), auction_id=1, item_id=itemId)

	return redirect("catalog")

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
