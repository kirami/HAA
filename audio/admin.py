from django.contrib import admin
from audio.models import Auction, Category, Item, Bid, Address, Label, UserProfile, Payment, Invoice
from audio.models import Consignor, Consignment

class BidAdmin(admin.ModelAdmin):

    list_display = ('user', 'item', 'amount',)
    search_fields = ['user__email', 'item__id']

admin.site.register(Auction)
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Bid, BidAdmin)
admin.site.register(Address)
admin.site.register(Label)
admin.site.register(UserProfile)
admin.site.register(Payment)
admin.site.register(Invoice)
admin.site.register(Consignor)
admin.site.register(Consignment)


