from django.contrib import admin
from audio.models import Auction, Category, Item, Bid, Address


class BidAdmin(admin.ModelAdmin):

    list_display = ('user', 'item', 'amount')

admin.site.register(Auction)
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Bid, BidAdmin)
admin.site.register(Address)