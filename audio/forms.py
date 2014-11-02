from django.forms import ModelForm, Form, MultipleChoiceField, DecimalField, ModelChoiceField, CharField
from audio.models import Address, Bid, Item, Consignment, Consignor
from audio.utils import *
import logging




# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create the form class.
class ContactForm(ModelForm):

	class Meta:
		model = Address
		exclude = ('user',)
		#fields = ['address_one', 'address_two', 'city', 'state', 'zipcode', 'postal_code', 'country', 'telephone', ]

class BidSubmitForm(ModelForm):
    lotId = CharField(label = "Lot ID:")
    class Meta:
		model = Bid
		exclude = ('user', 'date', 'winner', 'auction', 'item')
		
class SimpleBidForm(Form):
    lotId = CharField(label = "Lot ID:")
    

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
    		raise ValidationError(_('Invalid value'))

    	return data

    def clean(self):
    	self.clean_bcItemsSelected()
    	if 'bcItemsAvailable' in self._errors:
    		self.errors.pop('bcItemsAvailable')
    	if 'bcItemsSelected' in self._errors:
    		self.errors.pop('bcItemsSelected')
    	return self.cleaned_data

    