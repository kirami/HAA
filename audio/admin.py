from django.contrib import admin
from audio.models import Auction, Category, Item, Bid, Address, Label


class BidAdmin(admin.ModelAdmin):

    list_display = ('user', 'item', 'amount', 'second_chance_bid',)
    search_fields = ['user__email', 'item__id']

admin.site.register(Auction)
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Bid, BidAdmin)
admin.site.register(Address)
admin.site.register(Label)


