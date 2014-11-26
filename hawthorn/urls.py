from django.conf.urls import patterns, include, url

from django.contrib import admin
from audio import views
from audio import admin_views
admin.autodiscover()



urlpatterns = patterns('',

    #url(r'^blog/', include('blog.urls')),
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/report/(?P<auctionId>\d+)/$', admin_views.runReport, name='runReport'),
    #url(r'^admin/markWinners/(?P<auctionId>\d+)/$', admin_views.markWinners, name='markWinners'),
    url(r'^admin/winners/(?P<auctionId>\d+)/$', admin_views.winners, name='winners'),
    url(r'^admin/endBlindAuction/(?P<auctionId>\d+)/$', admin_views.endBlindAuction, name='endBlindAuction'),
    url(r'^admin/endFlatAuction/(?P<auctionId>\d+)/(?P<userId>\d+)', admin_views.endFlatAuction, name='endFlatAuction'),
    url(r'^admin/endFlatAuction/(?P<auctionId>\d+)/$', admin_views.endFlatAuction, name='endFlatAuction'),
    
    #url(r'^admin/createUser/$', admin_views.createUser, name='createUser'),
    #url(r'^admin/winners/$', admin_views.winners, name='winners'),
    url(r'^admin/losers/(?P<auctionId>\d+)/$', admin_views.losers, name='losers'),
    url(r'^admin/wonItems/(?P<auctionId>\d+)/$', admin_views.wonItems, name='wonItems'),
    url(r'^admin/unsoldItems/(?P<auctionId>\d+)/$', admin_views.unsoldItems, name='unsoldItems'), 
    url(r'^admin/bulkConsignment/(?P<auctionId>\d+)/$', admin_views.bulkConsignment, name='bulkConsignment'),
    url(r'^admin/balances/(?P<userId>\d+)', admin_views.userBalanceInfo, name='userBalanceInfo'),     
    url(r'^admin/balances/$', admin_views.calculateBalances, name='calculateBalances'),    
    url(r'^admin/sendEmail/$', admin_views.sendTemplateEmail, name='sendTemplateEmail'),
    url(r'^admin/getInvoices/(?P<auctionId>\d+)/(?P<userId>\d+)', admin_views.getInvoices, name='getInvoices'),
    url(r'^admin/invoices/(?P<auctionId>\d+)/$', admin_views.invoices, name='invoices'),
    url(r'^admin/createBid/(?P<auctionId>\d+)/$', admin_views.createBid, name='createBid'),
    url(r'^admin/userBreakdown/', admin_views.userBreakdown, name='userBreakdown'),
    url(r'^admin/sendInvoices/(?P<auctionId>\d+)', admin_views.sendInvoices, name='sendInvoices'),
    url(r'^admin/sendLoserLetters/(?P<auctionId>\d+)', admin_views.sendLoserLetters, name='sendLoserLetters'),
    url(r'^admin/endAuction/(?P<auctionId>\d+)/$', admin_views.endAuction, name='endAuction'),
    url(r'^admin/emailAdmin/(?P<auctionId>\d+)', admin_views.emailAdmin, name='emailAdmin'),
    url(r'^admin/sendConsignorEmails/$', admin_views.sendAllConsignorReports, name='sendAllConsignorReports'),
    url(r'^admin/consignorReport/(?P<auctionId>\d+)/(?P<consignorId>\d+)', admin_views.consignorReportById, name='consignorReportById'),   
    url(r'^admin/consignorReport/(?P<auctionId>\d+)/$', admin_views.consignorReport, name='consignorReport'),   
    url(r'^admin/', include(admin.site.urls)),
	url(r'^audio/', include('audio.urls')),

)

