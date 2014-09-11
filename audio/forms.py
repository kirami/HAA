from django.forms import ModelForm
from audio.models import Address, Bid

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