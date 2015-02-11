from django.contrib import admin
from audio.models import Auction, Category, Item, Bid, Address, Label, UserProfile, Payment, Invoice, Condition, PrintedCatalog
from audio.models import Consignor, Consignment
from django.conf.urls import patterns, url
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import admin
from django.http import HttpResponse
from django import forms



import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


UserAdmin.list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'date_joined')

class CustomConsignmentModelForm(forms.ModelForm):
    class Meta:
        model = Consignment
    def __init__(self, *args, **kwargs):
        super(CustomConsignmentModelForm, self).__init__(*args, **kwargs)
        self.fields['item'].queryset = Item.objects.filter(consignedItem=None)

        

class ConditionAdmin(admin.ModelAdmin):
    list_filter = ("auction",)
    list_display = ('user', 'message')

class BidAdmin(admin.ModelAdmin):

    list_display = ('user', 'item', 'amount', 'winner', )
    search_fields = ['user__email', 'item__lot_id', 'item__name', 'item__artist']
    list_filter = ('item__auction', 'winner',)

    raw_id_fields = ("item",)
    """
    def view_link(self, obj):
      return u"<a href='view/%d/'>View</a>" % obj.id
    view_link.short_description = ''
    view_link.allow_tags = True
    list_display = ('id', view_link(self, "1"))
    """


class InvoiceAdmin(admin.ModelAdmin):

    list_display = ('user', 'auction',)
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'user__username']
    list_filter = ('auction',)
    
class ItemAdmin(admin.ModelAdmin):

    list_display = ('name', 'lot_id', 'auction',)
    search_fields = ['name', 'lot_id']
    list_filter = ('auction',)

class PrintedCatalogAdmin(admin.ModelAdmin):

    list_display = ('user', 'auction',)
    search_fields = ['user']


class ConsignmentAdmin(admin.ModelAdmin):
    #form = CustomConsignmentModelForm
    list_display = ('item', 'consignor', 'minimum', 'maximum', 'percentage',)
    list_filter = ('item__auction', 'consignor',)
    search_fields = ['item__name', 'item__lot_id']


admin.site.register(Auction)
admin.site.register(Category)
admin.site.register(Item, ItemAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Address)
admin.site.register(Label)
admin.site.register(UserProfile)
admin.site.register(Payment)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Consignor)
admin.site.register(Consignment, ConsignmentAdmin)
admin.site.register(Condition, ConditionAdmin)
admin.site.register(PrintedCatalog, PrintedCatalogAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)




