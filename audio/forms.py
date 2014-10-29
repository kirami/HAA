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


class BulkConsignmentForm():
	percentage = DecimalField(max_digits=19, decimal_places=2)
	minimum = DecimalField(max_digits=19, decimal_places=2)
	maximum  = DecimalField(max_digits=19, decimal_places=2, required = False) 

class BulkConsignment(Form):
    choice = [(xt.id, xt.name) for xt in getNoBidItems(True) ]
    consignors = ModelChoiceField(Consignor.objects.all())
    bcItemsAvailable = MultipleChoiceField(choices=choice)	
    bcItemsSelected = MultipleChoiceField()
    
    data = {"percentage":25,"minimum":0,"maximum":10.00}
    range1 = BulkConsignmentForm()

    data = {"percentage":35,"minimum":10.01,"maximum":20}
    range2 = BulkConsignmentForm()

    data = {"percentage":45,"minimum":20.01,"maximum":None}
    range3 = BulkConsignmentForm()


    def save(self):
    	#todo get auction id
    	auctionId = 1
    	#logger.error(self.data)
    	percentage = self.data["percentage"]
    	
    	logger.error("perc: "+percentage.encode('utf-8'))
    	min = self.data["minimum"]
    	max = self.data["maximum"]
    	

    	for selected in self.data["bcItemsSelected"]:
    		item = Item.objects.get(id=selected)
    		Consignment.objects.create(item = item, auction_id = auctionId, percentage = percentage[0], minimum = min[0], maximum = max[0])

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

    