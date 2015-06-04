from django.forms import ModelForm, Form, MultipleChoiceField, DecimalField, ModelChoiceField, CharField, \
                 EmailField, DateTimeField, IntegerField, ChoiceField, FileField, BooleanField
from django.contrib.auth.forms import UserCreationForm
from audio.models import Address, Bid, Item, Consignment, Consignor, UserProfile, User, Auction, Category, Label, ItemType
from audio.utils import *
from audio.dropdowns import *
from django.core.exceptions import ValidationError
import logging

from datetime import datetime 

# Get an instance of a logger
logger = logging.getLogger(__name__)



class ItemPrePopulateForm(Form):
    auction = ModelChoiceField(Auction.objects.all().order_by("-id"))
     
    category = ModelChoiceField(Category.objects.all())
    label =  ModelChoiceField(Label.objects.all().order_by("name"))
    item_type =  ModelChoiceField(ItemType.objects.all())
    min_bid = DecimalField(label='Minumum Bid', initial=2.00)
    beginning_lot_id = IntegerField(label="Starting lot id", required=False)

    def __init__(self, auctionId = None, *args, **kwargs):
        super(ItemPrePopulateForm, self).__init__(*args, **kwargs)
        #TODO non deadbeat users etc
        if auctionId:
            self.fields['category'].queryset = self.fields['category'].queryset.filter(auction_id=auctionId)
            #self.fields['auction'] = Auction.objects.get(id = auctionId)

class InvoiceForm(ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoiced_amount', 'second_chance_invoice_amount', 'tax', 'second_chance_tax', 'discount', 'discount_percent']

#wrapper for item form in admin to order and filter
class ItemAdminForm(ModelForm):
    class Meta:
        model = Item

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', False)

        super(ItemAdminForm, self).__init__(*args, **kwargs)   
        if instance.auction:
            self.fields['category'].queryset = Category.objects.filter(auction = instance.auction).order_by('name')
        else:
            self.fields['category'].queryset = Category.objects.order_by('name')

class ItemForm(ModelForm):
   
    def __init__(self, *args, **kwargs):
        auctionId = kwargs.pop('auctionId',False)
        super(ItemForm, self).__init__(*args, **kwargs)
        
        #TODO non deadbeat users etc
        if auctionId:
            self.fields['category'].queryset = self.fields['category'].queryset.filter(auction_id=auctionId)
        self.fields['label'].queryset = self.fields['label'].queryset.order_by("name")
    
    class Meta:
        model = Item
        fields=[
            'lot_id',
            'label',
            'record_number',
            'record_number_two',
            'name',
            'artist',
            'notes',
            'name_two',
            'artist_two',
            'notes_two',
            'condition',
            'defect',
            'min_bid',
            'quantity',
            'category',
            'item_type',
            'auction',
            'image',
            'thumbnail',
            'prefix']

class UserForm(ModelForm):
    email = EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
       

class UserCreateForm(UserCreationForm):
    email = EmailField(required=True)
    pdf_list = BooleanField()
    courtesy_list = BooleanField()
    deadbeat = BooleanField()
    email_only = BooleanField()
    quiet = BooleanField()
    ebay = BooleanField()
    #notes = models.CharField(max_length=200, null = True, blank=True)
    verified = BooleanField()

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

class UserProfileForm(ModelForm):

    class Meta:
        model = UserProfile

class AdminBidForm(ModelForm):
    
    def __init__(self, auctionId, *args, **kwargs):
        super(AdminBidForm, self).__init__(*args, **kwargs)
        #TODO non deadbeat users etc
        if "item" in self.fields:
            self.fields['item'].queryset = self.fields['item'].queryset.filter(auction_id=auctionId)
        if "date" in self.fields:
            self.fields['date'] = DateTimeField(label="Date", initial=datetime.now())
        
        self.fields['amount'] = DecimalField(label='amount', initial=0.00)
        self.fields['user'].queryset = User.objects.order_by('username')
        self.fields['item'].queryset = Item.objects.order_by('lot_id')

        
    class Meta:
        model = Bid
        exclude = ('invoice',)

    def clean_item(self):
        
        item = self.cleaned_data["item"]
        bids = Bid.objects.filter(user=self.data["user"], item=item)
        if len(bids)> 0:
            bid = bids[0]
            raise ValidationError(('User has already bid on item: ' + str(item)),code='duplicate',params={'bid': bid.id})     
        return item

    def clean_amount(self):
        amount = self.data['amount']
        item = self.cleaned_data.get("item")
        
        if item and self.cleaned_data["amount"] < item.min_bid:
            raise ValidationError(('Min bid for this item is: $' + str(item.min_bid))) 
        return amount

    

    def save(self,  auctionId, commit=True):

        new_bid = super(AdminBidForm, self).save(commit=False)
        now = datetime.now()
        invoice = None
        invoices = Invoice.objects.filter(auction = auctionId, user = self.cleaned_data["user"])
        
        user = self.cleaned_data["user"]
        up = UserProfile.objects.get(user = user)
        if not up.billing_address or not up.shipping_address:
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
    
    def __init__(self,  *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)

        self.fields['state'] = ChoiceField(
            choices=getStates(), required=False )

        self.fields['country'] = ChoiceField(
            choices=getCountries())

    def clean_city(self):

        #logger.error("name: %s" % self.PREFIX_FIELD_NAME)
        if self.prefix:
            country = self.data[self.prefix + "-country"]
            city = self.data[self.prefix + "-city"]

        else:
            country = self.data["country"]
            city = self.data["city"]
            
        if country == "USA":
            if not city:
                raise ValidationError(('You must entery a city'))
        return city

    def clean_zipcode(self):
        if self.prefix:
            country = self.data[self.prefix + "-country"]
            zip = self.data[self.prefix + "-zipcode"]

        else:

            country = self.data["country"]
            zip = self.data["zipcode"]
        
        if country == "USA":
            if not zip:
                raise ValidationError(('You must entery a zipcode'))  
        return zip

    def clean_state(self):
        if self.prefix:
            country = self.data[self.prefix + "-country"]
            state = self.data[self.prefix + "-state"]

        else:
            country = self.data["country"]
            state = self.data["state"]
        
        if country == "USA":
            if not state:
                raise ValidationError(('You must entery a state')) 
        return state

class BulkConsignment(Form):
    from django import forms
    consignor = ModelChoiceField(Consignor.objects.all())
    bcItemsAvailable = MultipleChoiceField(required=False)	
    #bcItemsSelected = MultipleChoiceField(widget=forms.RadioSelect)
    bcItemsSelected = MultipleChoiceField(widget=forms.SelectMultiple())
    
    def __init__(self,*args,**kwargs):
        auctionId = kwargs.pop("auctionId")     # client is the parameter passed from views.py
        super(BulkConsignment, self).__init__(*args,**kwargs)
        choice = [(xt.id, xt.name) for xt in getNoBidItems(auctionId, True) ]
        self.fields["bcItemsAvailable"] = MultipleChoiceField(choices=choice, required=False)
        
    def save(self):
    	consignor = self.data["consignor"]
    	total = int(self.data["totalConsignments"])
    	
    	for selected in self.data.getlist("bcItemsSelected"):
            index = 1
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


    def clean(self):
            
    	if 'bcItemsSelected' in self._errors:
    		self.errors.pop('bcItemsSelected')
    	return self.cleaned_data
        
        

    