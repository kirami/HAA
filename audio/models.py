
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Auction(models.Model):
	start_date = models.DateTimeField()
	end_date = models.DateTimeField()
	second_chance_start_date = models.DateTimeField(null = True)
	second_chance_end_date = models.DateTimeField(null = True)
	#flat_bid_amount = models.DecimalField(max_digits=19, decimal_places=2, default=2.00)
	blind_locked = models.BooleanField(default = False)
	flat_locked = models.BooleanField(default = False)
	name = models.CharField(max_length=200, blank=True, null=True)
	description = models.TextField( default="", null = True, blank = True)

	def __str__(self):
		return  str(self.name)

class Invoice(models.Model):
	user = models.ForeignKey(User, related_name="userInvoice")
	auction = models.ForeignKey(Auction)
	invoiced_amount = models.DecimalField(max_digits=19, decimal_places=2)
	invoice_date = models.DateField(null = True, blank = True)
	reminder_invoice_date = models.DateField(null = True, blank = True)
	second_chance_invoice_amount = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	second_chance_invoice_date= models.DateField(null = True, blank = True)
	shipped_date = models.DateField(null = True, blank=True)
	on_hold = models.BooleanField(default = False)
	shipping = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	second_chance_shipping = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	tax = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	second_chance_tax = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	discount = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	discount_percent = models.DecimalField(max_digits=19, decimal_places=2, default=0)

	def __str__(self):
		return str("%s - %s" % (self.user,  self.auction.name))

	#on hold

class Payment(models.Model):
	amount = models.DecimalField(max_digits=19, decimal_places=2)
	#auction?
	payment_type = models.CharField(max_length=100)
	user = models.ForeignKey(User, related_name="paymentUser")
	invoice = models.ForeignKey(Invoice, related_name = "paymentInvoice")
	date_received = models.DateField()

	def __str__(self):
		return str(self.invoice)

class Category(models.Model):
	name = models.CharField(max_length=100)
	description = models.CharField(max_length=450)
	min_bid = models.DecimalField(max_digits=19, decimal_places=2, null = True, blank = True)
	auction = models.ForeignKey(Auction)
	order_number = models.IntegerField(default=None)


	def __str__(self):
		return str(self.name)

	class Meta:
		verbose_name_plural = "Categories"

class Label(models.Model):
	name = models.CharField(max_length=100)
	abbreviation = models.CharField(max_length=100)
	parent = models.CharField(max_length=100)

	def __str__(self):
		return self.name

class ItemType(models.Model):
	name = models.CharField(max_length=200, default="")
	notes = models.CharField(max_length=200, default="", null = True, blank = True)

	def __str__(self):
		return str(self.name)
        
class Item(models.Model):
	#TODO fix requireds
	label = models.ForeignKey(Label, null = True, blank=True, related_name="itemLabel")
	artist = models.CharField(max_length=400, null = True, blank = True)
	artist_two = models.CharField(max_length=400, null = True, blank = True)
	name = models.CharField(max_length=400, default="")
	name_two = models.CharField(max_length=400, null = True, blank = True)
	notes = models.CharField(max_length=800, default="", null = True, blank = True)
	notes_two = models.CharField(max_length=800, default="", null = True, blank = True)
	record_number = models.CharField(max_length=100, null = True, blank = True)
	record_number_two = models.CharField(max_length=100, null = True, blank = True)
	min_bid = models.DecimalField(max_digits=19, decimal_places=2)
	lot_id = models.IntegerField(null = True, blank=True)
	category = models.ForeignKey(Category, related_name="itemCategory")
	item_type = models.ForeignKey(ItemType, related_name="itemType")
	condition = models.CharField(max_length=100, default="")
	defect = models.CharField(max_length=100, default="", null = True, blank=True)
	quantity = models.IntegerField(default = 1)
	auction = models.ForeignKey(Auction, related_name="itemAuction")
	thumbnail = models.FileField(upload_to='items/', null = True, blank=True)
	image = models.FileField(upload_to='items/', null = True, blank=True)
	prefix = models.CharField(max_length=600, null = True, blank = True)

	
	class Meta:
		unique_together = (("auction", "lot_id"),)

	def __str__(self):
		return str(self.lot_id) + " " + self.name

class Bid(models.Model):
	user = models.ForeignKey(User, related_name="bidUser")
	date = models.DateTimeField()
	item = models.ForeignKey(Item,  related_name='bidItem')
	amount = models.DecimalField(max_digits=19, decimal_places=2, default=2.00)
	winner = models.BooleanField(default = False)
	invoice = models.ForeignKey(Invoice, null = True, blank = True, on_delete=models.SET_NULL)


	def __str__(self):
		return str(self.user)
	
	class Meta:
		unique_together = (("user", "item"),)



class Address(models.Model):
	address_one = models.CharField(max_length=100, default="")
	address_two = models.CharField(max_length=100, null = True, blank=True)
	address_three = models.CharField(max_length=100, null = True, blank=True)
	city = models.CharField(max_length=100, null=True, blank=True)
	state = models.CharField(max_length=100, null=True, blank=True)
	zipcode = models.CharField(max_length=100, default="", null=True, blank=True)
	postal_code = models.CharField(max_length=100, null=True, blank=True)
	country = models.CharField(max_length=100, default="")
	telephone = models.CharField(max_length=100, default="")
	fax = models.CharField(max_length=100, null=True, blank=True)

	class Meta:
		verbose_name_plural = "Addresses"

	def __str__(self):
		return str(self.id) + "--"+self.address_one

class UserProfile(models.Model):
	user = models.ForeignKey(User, unique = True, related_name="upUser")
	pdf_list = models.BooleanField(default = False)
	courtesy_list = models.BooleanField(default = False)
	deadbeat = models.BooleanField(default=False)
	email_only = models.BooleanField(default=True)
	quiet = models.BooleanField(default = False)
	ebay = models.BooleanField(default = False)
	notes = models.CharField(max_length=200, null = True, blank=True)
	verified = models.BooleanField(default=False)
	confirmation_code = models.CharField(max_length=200, null = True, blank=True)
	shipping_address = models.ForeignKey(Address, related_name="upShipping", blank=True, null=True, on_delete=models.SET_NULL)
	billing_address = models.ForeignKey(Address, related_name="upBilling", blank=True, null=True, on_delete=models.SET_NULL)

	def __str__(self):
		return str(self.user)

class PrintedCatalog(models.Model):
	user = models.ForeignKey(User, related_name="pcUser")
	auction = models.IntegerField()

	def __str__(self):
		return str(self.user)
	


class Consignor(models.Model):
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	email = models.CharField(max_length=100)
	address = models.ForeignKey(Address, blank=True, null=True)

	def __str__(self):
		return str(self.first_name + " " + self.last_name)

class Consignment(models.Model):
	item = models.ForeignKey(Item, related_name="consignedItem")
	consignor = models.ForeignKey(Consignor, related_name="consignmentConsignor")
	percentage = models.DecimalField(max_digits=19, decimal_places=2)
	minimum = models.DecimalField(max_digits=19, decimal_places=2)
	maximum  = models.DecimalField(max_digits=19, decimal_places=2, blank  = True, null=True)

	def __str__(self):
		return str(self.item.name)

	class Meta:
		unique_together = (("minimum", "item"), ("maximum", "item"),)

class Condition(models.Model):
	user = models.ForeignKey(User)
	auction = models.ForeignKey(Auction)
	message = models.CharField(max_length=250, default="")
	done = models.BooleanField(default = False)


