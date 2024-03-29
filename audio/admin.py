from django.contrib import admin
from audio.models import Auction, Category, Item, Bid, Address, Label, UserProfile, \
Payment, Invoice, Condition, PrintedCatalog, ItemType
from audio.models import Consignor, Consignment
from django.conf.urls import patterns, url
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import admin
from django.http import HttpResponse
from django import forms
from audio.forms import ItemAdminForm

from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


UserAdmin.list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'date_joined', 'last_login')

UserAdmin.save_on_top = True


class InvoiceFilter(SimpleListFilter):
    title="No Shipping"
    parameter_name = 'shipped_date'

    def lookups(self, request, model_admin):
     return (
                ('Null', _('Not shipped yet')),
                ('Not Null', _('Already shipped')),
            )

    def queryset(self, request, queryset):
        if self.value() == 'Null':
            return queryset.filter(shipped_date = None)
        if self.value() == 'Not Null':
            return queryset.filter(shipped_date__isnull = False)


class ItemFilter(SimpleListFilter):
    title="No Bids"
    parameter_name = 'bidItem'

    def lookups(self, request, model_admin):
     return (
                ('Null', _('No bids')),
                ('Not Null', _('Has bids')),
            )

    def queryset(self, request, queryset):
        if self.value() == 'Null':
            return queryset.filter(bidItem = None)
        if self.value() == 'Not Null':
            return queryset.filter(bidItem__isnull = False).distinct()

        

class ConditionAdmin(admin.ModelAdmin):
    list_filter = ("auction", "done")
    list_display = ('user', 'message' ,"done")

class BidAdmin(admin.ModelAdmin):

    list_display = ('user', 'item', 'amount', 'winner', 'date',)
    search_fields = ['user__email', 'item__lot_id', 'item__name', 'item__artist', 'user__username', 'user__last_name', 'date']
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

    list_display = ('user', 'auction', 'invoice_date',)
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'user__username']
    list_filter = ('auction', 'on_hold', InvoiceFilter)
    
class ItemAdmin(admin.ModelAdmin):

    list_display = ('name', 'lot_id', 'auction')
    search_fields = ['name', 'lot_id']
    list_filter = ( 'item_type', "auction", ItemFilter)
    save_on_top = True
    ordering = ("lot_id", "label__name")
    form = ItemAdminForm



    #def changelist_view(self, request, extra_context=None):
    #    logger.error("request %s" % request)
    #    return super(ItemAdmin, self).changelist_view(request, extra_context=extra_context)

class PrintedCatalogAdmin(admin.ModelAdmin):

    list_display = ('user', 'auction',)
    search_fields = ['user']


class ConsignmentAdmin(admin.ModelAdmin):
    #form = CustomConsignmentModelForm
    list_display = ('item', 'consignor', 'minimum', 'maximum', 'percentage',)
    list_filter = ('item__auction', 'consignor',)
    search_fields = ['item__name', 'item__lot_id']

class CategoryAdmin(admin.ModelAdmin):
    #form = CustomConsignmentModelForm
    list_display = ('name', 'order_number', )
    list_filter = ('auction', )

class UserProfileAdmin(admin.ModelAdmin):
    #form = CustomConsignmentModelForm
    search_fields = ['user__email', "user__username"]
    list_filter = ('deadbeat', 'email_only', 'quiet', 'pdf_list',)
    #list_filter("deadbeat", )

class AddressAdmin(admin.ModelAdmin):
    search_fields = ['upBilling__user__email', 'upShipping__user__email', \
    'upBilling__user__username', 'upShipping__user__username', 'upBilling__user__first_name', 'upBilling__user__last_name' , \
    'upShipping__user__first_name', 'upShipping__user__last_name']
    
    list_display = ("id","get_author",  )
    def get_author(self, obj):
        ups = UserProfile.objects.filter(shipping_address = obj.id)
        #logger.error("user: %s" % ups[0].user)
        if len(ups) > 0:
            return "%s" % ups[0].user
        else:
            return None
    get_author.short_description = 'User'

class LabelAdmin(admin.ModelAdmin):
    search_fields = ['name', "abbreviation"]

admin.site.register(Auction)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Label, LabelAdmin)
admin.site.register(ItemType)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Payment)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Consignor)
admin.site.register(Consignment, ConsignmentAdmin)
admin.site.register(Condition, ConditionAdmin)
admin.site.register(PrintedCatalog, PrintedCatalogAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)




