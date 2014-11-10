from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Auction(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()
	second_chance_end_date = models.DateField(null = True)
	flat_bid_amount = models.DecimalField(max_digits=19, decimal_places=2, default=2.00)
	locked = models.BooleanField(default = False)

	def __unicode__(self):
		return u"%s" % self.id
'''
from django.contrib.admin.filterspecs import FilterSpec, RelatedFilterSpec
 

class CustomFilterSpec(RelatedFilterSpec):
    def __init__(self, *args, **kwargs):
        super(CustomFilterSpec, self).__init__(*args, **kwargs)       
        self.lookup_choices = Item.objects.filter(auction=1) #this method returns the dynamic list
 
FilterSpec.filter_specs.insert(0, (lambda f: bool(f.rel and hasattr(f, 'custom_filter_spec')), CustomFilterSpec))
''' 

class Invoice(models.Model):
	user = models.ForeignKey(User)
	auction = models.ForeignKey(Auction)
	invoiced_amount = models.DecimalField(max_digits=19, decimal_places=2)
	invoice_date = models.DateField()
	reminder_invoice_date = models.DateField()
	second_chance_invoice_amount = models.DateField()
	second_chance_invoice_date= models.DateField()

class Payment(models.Model):
	amount = models.DecimalField(max_digits=19, decimal_places=2)
	#auction?
	payment_type = models.CharField(max_length=100)
	user = models.ForeignKey(User)
	invoice = models.ForeignKey(Invoice)
	received_date = models.DateField()

class Category(models.Model):
	name = models.CharField(max_length=100)

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name_plural = "Categories"

class Label(models.Model):
	name = models.CharField(max_length=100)
	abbreviation = models.CharField(max_length=100)
	parent = models.CharField(max_length=100)

	def __unicode__(self):
		return self.name

        
class Item(models.Model):
	#TODO fix requireds
	label = models.ForeignKey(Label, null = True)
	name = models.CharField(max_length=200, default="")
	record_number = models.CharField(max_length=100, null = True, blank = True)
	min_bid = models.DecimalField(max_digits=19, decimal_places=2)
	lot_id = models.IntegerField(null = True, blank=True, default=" ")
	category = models.ForeignKey(Category)
	condition = models.CharField(max_length=100, default="")
	quantity = models.IntegerField(default = 1)
	auction = models.ForeignKey(Auction)
	
	class Meta:
		unique_together = (("auction", "lot_id"),)

	def __unicode__(self):
		return str(self.lot_id) + " " + self.name

class Bid(models.Model):
	user = models.ForeignKey(User)
	date = models.DateField()
	item = models.ForeignKey(Item)
	amount = models.DecimalField(max_digits=19, decimal_places=2, default=2.00)
	winner = models.BooleanField(default = False)
	#item.custom_filter_spec = True
	
	#won bid?
	#pay date
	#invoice sent

	def __unicode__(self):
		return unicode(self.user)
	
	class Meta:
		unique_together = (("user", "item"),)

class UserProfile(models.Model):
	user = models.ForeignKey(User)
	#TODO defaults?
	pdf_list = models.BooleanField(default = False)
	printed_list = models.BooleanField(default = False)
	courtesy_list = models.BooleanField(default = False)
	deadbeat = models.BooleanField(default=False)
	email_invoice = models.BooleanField(default=True)

class Address(models.Model):
	user = models.ForeignKey(User)
	address_one = models.CharField(max_length=100, default="")
	address_two = models.CharField(max_length=100, null = True, blank=True)
	city = models.CharField(max_length=100)
	state = models.CharField(max_length=100)
	zipcode = models.CharField(max_length=100, default="")
	postal_code = models.CharField(max_length=100, null=True, blank=True)
	country = models.CharField(max_length=100, default="")
	telephone = models.CharField(max_length=100, null=True, blank = True)
	cell_phone = models.CharField(max_length=100, null=True, blank=True)
	fax = models.CharField(max_length=100, null=True, blank=True)

	class Meta:
		verbose_name_plural = "Addresses"

	def __unicode__(self):
		return self.user.email + " "+self.user.first_name + " " + self.user.last_name

class Consignor(models.Model):
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	email = models.CharField(max_length=100)
	address = models.ForeignKey(Address, blank=True, null=True)

	def __unicode__(self):
		return self.first_name + " " + self.last_name

class Consignment(models.Model):
	item = models.ForeignKey(Item)
	consignor = models.ForeignKey(Consignor)
	percentage = models.DecimalField(max_digits=19, decimal_places=2)
	minimum = models.DecimalField(max_digits=19, decimal_places=2)
	maximum  = models.DecimalField(max_digits=19, decimal_places=2, blank  = True, null=True)

	def __unicode__(self):
		return self.item.name

