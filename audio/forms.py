from django.forms import ModelForm, Form, MultipleChoiceField, DecimalField, ModelChoiceField, CharField, \
                 EmailField, DateTimeField, IntegerField, ChoiceField
from django.contrib.auth.forms import UserCreationForm
from audio.models import Address, Bid, Item, Consignment, Consignor, UserProfile, User, Auction
from audio.utils import *
from audio.dropdowns import *
from django.core.exceptions import ValidationError
import logging

from datetime import datetime 

# Get an instance of a logger
logger = logging.getLogger(__name__)


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

class UserCreateForm(UserCreationForm):
    email = EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        new_user = super(UserCreateForm, self).save(commit=False)
        new_user.email = self.cleaned_data["email"]
        if commit:
            new_user.save()
            profile = UserProfile.objects.create(user = new_user)
        return new_user


class AdminBidForm(ModelForm):
    
    def __init__(self, auctionId, *args, **kwargs):
        super(AdminBidForm, self).__init__(*args, **kwargs)
        #TODO non deadbeat users etc
        if "item" in self.fields:
            self.fields['item'].queryset = self.fields['item'].queryset.filter(auction_id=auctionId)
        if "date" in self.fields:
            self.fields['date'] = DateTimeField(label="Date", initial=datetime.now())
        
        self.fields['amount'] = DecimalField(label='amount', initial=0.00)

        
    class Meta:
        model = Bid
        exclude = ('invoice',)

    def clean_amount(self):
        amount = self.data['amount']
        item = self.cleaned_data["item"]
        
        if self.cleaned_data["amount"] < item.min_bid:
            raise ValidationError(('Min bid for this item is: $' + str(item.min_bid))) 
        return amount

    def save(self,  auctionId, commit=True):

        new_bid = super(AdminBidForm, self).save(commit=False)
        now = datetime.now()
        invoice = None
        invoices = Invoice.objects.filter(auction = auctionId, user = self.cleaned_data["user"])
        
        user = self.cleaned_data["user"]
        addresses = Address.objects.filter(user = user)

        if len(addresses) < 1:
            raise ValidationError(('This user has no address')) 
        
        if invoices:
            invoice = invoices[0]
        auction = Auction.objects.get(id = auctionId)
        
            #if is blind
        if now < auction.end_date:
            #TODO if is locked?
            if invoice != None:
                raise ValidationError(('Trying to add a blind bid but user already has invoice for this auction'))    
        #if is second chance
        #TODO auto do min bid?
        if now > auction.end_date and now < auction.second_chance_end_date:
            if invoice != None and invoice.second_chance_invoice_date != None:
                raise ValidationError(('Trying to add a flat bid but user already has second invoice for this auction'))    


        new_bid.save()
        return new_bid

class BidSubmitForm(ModelForm):
    #email = EmailField(required=True)
    lotId = CharField(label = "Lot ID:")
    
    def __init__(self, auctionId, *args, **kwargs):
        super(BidSubmitForm, self).__init__(*args, **kwargs)
        self.auction = Auction.objects.get(id = auctionId)

    class Meta:
        model = Bid
        exclude = ('user', 'date', 'winner', 'auctionId', 'item', 'invoice')

    def save(self, commit=True):
        logger.error("1")
        new_bid = super(BidSubmitForm, self).save(commit=False)
        lotId = self.cleaned_data["lotId"]
        items = Item.objects.filter(lot_id = lotId, auction = self.auction)
         
        if len(items) < 1:
            raise ValidationError('There is no item with lot ID %s' % lotId)

        new_bid.item = items[0]
        
        if commit:
            
            new_bid.save()
        return new_bid

    def clean_lotId(self):
        lotId = self.data["lotId"]
        if lotId is None:
            raise ValidationError('You must enter a lot ID.')
            return lotId
    
        items = Item.objects.filter(lot_id = lotId, auction = self.auction)

        if len(items) < 1:
            raise ValidationError('There is no item with lot ID %s' % lotId)
            return lotId

        return lotId

    def clean_amount(self):

        amount = self.data['amount']
        
        if amount == None:
            raise ValidationError('Invalid bid')

        lotId = self.data["lotId"]
        if not lotId:
            return amount

        items = Item.objects.filter(lot_id = lotId, auction = self.auction)

        if len(items) < 1:
            return amount

        item = items[0]

        if self.cleaned_data["amount"] < item.min_bid:
            raise ValidationError(('Min bid for this item is: $' + str(item.min_bid))) 

        return amount

class ContactForm(ModelForm):

    class Meta:
        model = Address
        exclude = ('user',)
        #fields = ['address_one', 'address_two', 'city', 'state', 'zipcode', 'postal_code', 'country', 'telephone', ]
    
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['state'] = ChoiceField(
            choices=getStates(), required=False )

        self.fields['country'] = ChoiceField(
            choices=getCountries())

class BulkConsignment(Form):
    consignor = ModelChoiceField(Consignor.objects.all())
    bcItemsAvailable = MultipleChoiceField()	
    bcItemsSelected = MultipleChoiceField()
    
    def __init__(self,*args,**kwargs):
        auctionId = kwargs.pop("auctionId")     # client is the parameter passed from views.py
        super(BulkConsignment, self).__init__(*args,**kwargs)
        choice = [(xt.id, xt.name) for xt in getNoBidItems(auctionId, True) ]
        self.fields["bcItemsAvailable"] = MultipleChoiceField(choices=choice)
        
    def save(self):
    	consignor = self.data["consignor"]
    	total = int(self.data["totalConsignments"])
    	index = 1

    	for selected in self.data["bcItemsSelected"]:
    		while index<=total:
	    		min = self.data["min" + str(index)]
	    		max = self.data["max" + str(index)]
    	
	    		if index == 1:
	    			min = 0
	    		
	    		if index == 3:
	    			max = None

	    		percent = self.data["percent"+ str(index)]
	    		
	    		item = Item.objects.get(id=selected)
	    		Consignment.objects.create(item = item, percentage = percent, minimum = min, maximum = max, consignor_id = consignor)
	    		index = index + 1

    def clean_bcItemsSelected(self):
    	logger.error("cleaning selected")
    	data = self.data['bcItemsSelected']
    	
    	if data == None:
    		raise ValidationError('Invalid value')

    	return data

    def clean(self):
    	self.clean_bcItemsSelected()
    	if 'bcItemsAvailable' in self._errors:
    		self.errors.pop('bcItemsAvailable')
    	if 'bcItemsSelected' in self._errors:
    		self.errors.pop('bcItemsSelected')
    	return self.cleaned_data

    