from django.forms import ModelForm, Form, MultipleChoiceField, DecimalField, ModelChoiceField
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

	class Meta:
		model = Bid
		exclude = ('user', 'date',)
		#fields = ['address_one', 'address_two', 'city', 'state', 'zipcode', 'postal_code', 'country', 'telephone', ]


class BulkConsignment(Form):
    choice = [(xt.id, xt.name) for xt in getNoBidItems(True) ]
    consignor = ModelChoiceField(Consignor.objects.all())
    bcItemsAvailable = MultipleChoiceField(choices=choice)	
    bcItemsSelected = MultipleChoiceField()
     

    def save(self):
    	#todo get auction id
    	auctionId = 1
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
	    		Consignment.objects.create(item = item, auction_id = auctionId, percentage = percent, minimum = min, maximum = max, consignor_id = consignor)
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

    