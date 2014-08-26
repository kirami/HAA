from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Auction(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()

class Category(models.Model):
	name = models.CharField(max_length=100)

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name_plural = "Categories"
        
class Item(models.Model):
	min_bid = models.DecimalField(max_digits=19, decimal_places=2)
	lot_id = models.IntegerField()
	category = models.ForeignKey(Category)
	#condition = models.CharField(max_length=100)

class Bid(models.Model):
	user = models.ForeignKey(User)
	date = models.DateField()
	auction = models.ForeignKey(Auction)
	item = models.ForeignKey(Item)
	amount = models.DecimalField(max_digits=19, decimal_places=2, default=2.00)

class UserProfile(models.Model):
	user = models.ForeignKey(User)
	pdf_list = models.BooleanField(default = False)
	printed_list = models.BooleanField(default = False)
	courtesy_list = models.BooleanField(default = False)
	deadbeat = models.BooleanField(default=True)

class Address(models.Model):
	user = models.ForeignKey(User)
	address_one = models.CharField(max_length=100, default="")
	address_two = models.CharField(max_length=100, null = True)
	city = models.CharField(max_length=100)
	state = models.CharField(max_length=100)
	zipcode = models.PositiveIntegerField()
	postal_code = models.CharField(max_length=100, null=True)
	country = models.CharField(max_length=100, default="")
	telephone = models.CharField(max_length=100, null=True)
	cell_phone = models.CharField(max_length=100, null=True)
	fax = models.CharField(max_length=100, null=True)

	class Meta:
		verbose_name_plural = "Addresses"

	def __unicode__(self):
		return self.user.email



