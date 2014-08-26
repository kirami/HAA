from django.contrib import admin
from audio.models import Auction, Category, Item, Bid, Address

admin.site.register(Auction)
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Bid)
admin.site.register(Address)