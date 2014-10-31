from django.contrib import admin
from audio.models import Auction, Category, Item, Bid, Address, Label, UserProfile, Payment, Invoice
from audio.models import Consignor, Consignment

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class BidAdmin(admin.ModelAdmin):

    list_display = ('user', 'item', 'amount', )
    search_fields = ['user__email', 'item__lot_id']
    list_filter = ('item__auction',)

    raw_id_fields = ("item",)

    '''
    def __init__(self, *args, **kwargs):
        super(BidAdmin, self).__init__(*args, **kwargs)
        logger.error("kwargs")
        logger.error(self.fields['user'])
        #self.fields['item'].queryset = Item.objects.filter(auction=1)
        #logger.error("kwargs")
        #logger.error(self.fields['item'])
    '''


class ItemAdmin(admin.ModelAdmin):

    list_display = ('name', 'lot_id', 'auction',)
    search_fields = ['name', 'lot_id']
    list_filter = ('auction',)


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
admin.site.register(Consignment)


