from django.contrib import admin
from audio.models import Auction, Category, Item, Bid, Address, Label, UserProfile, Payment, Invoice
from audio.models import Consignor, Consignment
from django.conf.urls import patterns, url

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.contrib import admin
from django.http import HttpResponse



class BidAdmin(admin.ModelAdmin):

    list_display = ('user', 'item', 'amount', )
    search_fields = ['user__email', 'item__lot_id']
    list_filter = ('item__auction',)

    raw_id_fields = ("item",)
    """
    def view_link(self, obj):
      return u"<a href='view/%d/'>View</a>" % obj.id
    view_link.short_description = ''
    view_link.allow_tags = True
    list_display = ('id', view_link(self, "1"))
    """

    
class ItemAdmin(admin.ModelAdmin):

    list_display = ('name', 'lot_id', 'auction',)
    search_fields = ['name', 'lot_id']
    list_filter = ('auction',)


class ConsignmentAdmin(admin.ModelAdmin):

    list_display = ('item', 'consignor', 'minimum', 'maximum', 'percentage',)
    list_filter = ('item__auction',)


admin.site.register(Auction)
admin.site.register(Category)
admin.site.register(Item, ItemAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Address)
admin.site.register(Label)
admin.site.register(UserProfile)
admin.site.register(Payment)
admin.site.register(Invoice)
admin.site.register(Consignor)
admin.site.register(Consignment, ConsignmentAdmin)


