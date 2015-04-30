from django.conf.urls import patterns, include, url

from django.contrib import admin
from audio import views
from audio import admin_views
from django.views.generic import TemplateView
admin.autodiscover()



urlpatterns = patterns('',

    #url(r'^blog/', include('blog.urls')),
    #url(r'^admin/', include(admin.site.urls)),
      
    url(r'^admin/sendWinningBidReport/$', admin_views.sendWinningBidReport, name='sendWinningBidReport'),
    
    url(r'^admin/winningBidReport/(?P<auctionId>\d+)/$', admin_views.winningBidReport, name='winningBidReport'),
    url(r'^admin/conditions/(?P<auctionId>\d+)/$', admin_views.conditionsCheck, name='conditionsCheck'),
    url(r'^admin/report/(?P<auctionId>\d+)/$', admin_views.runReport, name='runReport'),
    #url(r'^admin/markWinners/(?P<auctionId>\d+)/$', admin_views.markWinners, name='markWinners'),
    url(r'^admin/winners/(?P<auctionId>\d+)/$', admin_views.winners, name='winners'),
    url(r'^admin/endBlindAuction/(?P<auctionId>\d+)/$', admin_views.endBlindAuction, name='endBlindAuction'),
    url(r'^admin/endFlatAuction/(?P<auctionId>\d+)/(?P<userId>\d+)', admin_views.endFlatAuction, name='endFlatAuction'),
    url(r'^admin/endFlatAuction/(?P<auctionId>\d+)/$', admin_views.endFlatAuction, name='endFlatAuction'),
    url(r'^admin/runningTotal/(?P<auctionId>\d+)/$', admin_views.getRunningBidTotal, name='getRunningBidTotal'),
    url(r'^admin/endSSAuction/(?P<auctionId>\d+)/(?P<userId>\d+)', admin_views.endSSAuction, name='endSSAuction'),
    url(r'^admin/paidNotShipped/(?P<auctionId>\d+)/$', admin_views.getPaidUnshipped, name='getPaidUnshipped'),
    url(r'^admin/markShipped/(?P<auctionId>\d+)/$', admin_views.markShipped, name='markShipped'),

    #url(r'^admin/createUser/$', admin_views.createUser, name='createUser'),
    #url(r'^admin/winners/$', admin_views.winners, name='winners'),
    url(r'^admin/losers/(?P<auctionId>\d+)/$', admin_views.losers, name='losers'),
    url(r'^admin/wonItems/(?P<auctionId>\d+)/$', admin_views.wonItems, name='wonItems'),
    url(r'^admin/unsoldItems/(?P<auctionId>\d+)/$', admin_views.unsoldItems, name='unsoldItems'), 
    url(r'^admin/bulkConsignment/(?P<auctionId>\d+)/$', admin_views.bulkConsignment, name='bulkConsignment'),
       
    url(r'^admin/userBalances/(?P<userId>\d+)', admin_views.userBalanceInfo, name='userBalanceInfo'), 
    url(r'^admin/balances/(?P<auctionId>\d+)', admin_views.calculateBalances, name='calculateBalances'),   
    url(r'^admin/balances/$', admin_views.calculateBalances, name='calculateBalances'), 

    url(r'^admin/sendEmail/$', admin_views.sendTemplateEmail, name='sendTemplateEmail'),
    url(r'^admin/getInvoices/(?P<auctionId>\d+)/(?P<userId>\d+)', admin_views.getInvoices, name='getInvoices'),
    #url(r'^admin/printInvoices/(?P<auctionId>\d+)/(?P<printIt>\d+)', admin_views.getInvoices, name='getInvoices'),
    url(r'^admin/printInvoices/(?P<auctionId>\d+)/(?P<userId>\d+)/$', admin_views.printInvoices, name='printInvoices'),
    url(r'^admin/printInvoices/(?P<auctionId>\d+)/$', admin_views.printInvoices, name='printInvoices'),
   
    url(r'^admin/invoices/(?P<auctionId>\d+)/$', admin_views.invoices, name='invoices'),
    url(r'^admin/createBid/(?P<auctionId>\d+)/$', admin_views.createBid, name='createBid'),
    url(r'^admin/userBreakdown/(?P<auctionId>\d+)/$', admin_views.userBreakdown, name='userBreakdown'),
    url(r'^admin/userBreakdown/$', admin_views.userBreakdown, name='userBreakdown'),
    url(r'^admin/sendInvoices/$', admin_views.sendInvoices, name='sendInvoices'),
    url(r'^admin/sendReminder/$', admin_views.sendReminder, name='sendReminder'),
    url(r'^admin/sendLoserLetters/(?P<auctionId>\d+)', admin_views.sendLoserLetters, name='sendLoserLetters'),
    url(r'^admin/endAuction/(?P<auctionId>\d+)/$', admin_views.endAuction, name='endAuction'),
    url(r'^admin/emailAdmin/(?P<auctionId>\d+)', admin_views.emailAdmin, name='emailAdmin'),
    url(r'^admin/sendConsignorEmails/$', admin_views.sendAllConsignorReports, name='sendAllConsignorReports'),
    url(r'^admin/consignorReport/(?P<auctionId>\d+)/(?P<consignorId>\d+)', admin_views.consignorReportById, name='consignorReportById'),   
    url(r'^admin/consignorReport/(?P<auctionId>\d+)/$', admin_views.consignorReport, name='consignorReport'),   
    url(r'^admin/shippingByInvoice/(?P<auctionId>\d+)/flatOnly/$', admin_views.shippingByInvoiceFlat, name='shippingByInvoiceFlat'),
    url(r'^admin/shippingByInvoice/(?P<auctionId>\d+)/filtered/$', admin_views.shippingByInvoiceFiltered, name='shippingByInvoiceFiltered'), 
    url(r'^admin/shippingByInvoice/(?P<auctionId>\d+)/$', admin_views.shippingByInvoice, name='shippingByInvoice'),    
    url(r'^admin/createUser/', admin_views.createUser, name='createUser'),
   
    #url(r'^admin/lookupItemWinner/(?P<auctionId>\d+)/(?P<itemId>\d+)', admin_views.lookupItemWinner, name='lookupItemWinner'),   
    #url(r'^admin/lookupItemWinner/(?P<auctionId>\d+)/$', admin_views.lookupItemWinner, name='lookupItemWinner'),   
    
    url(r'^admin/filterAdminIndex/$', admin_views.filterAdminIndex, name='filterAdminIndex'),  
    url(r'^admin/importUsers/', admin_views.importAdmin, name='importAdmin'),
    url(r'^admin/importUserEmail/', admin_views.importUserEmail, name='importUserEmail'),
    url(r'^admin/printLabels/(?P<auctionId>\d+)/(?P<labelType>\w+)/$', admin_views.printLabels, name='printLabels'),
    url(r'^admin/printLabels/(?P<auctionId>\d+)/$', admin_views.printLabels, name='printLabels'),
    url(r'^admin/addItem/$', admin_views.addItem, name='addItem'),  
    url(r'^admin/addItemUrl/$', admin_views.addItemPrepop, name='addItemPrepop'),  
    url(r'^admin/setDiscount/(?P<invoiceId>\d+)/$', admin_views.setDiscount, name='setDiscount'),  
    url(r'^admin/itemPrintOut/(?P<auctionId>\d+)/$', admin_views.itemPrintOut, name='itemPrintOut'),
    url(r'^admin/adjustLotIds/(?P<auctionId>\d+)/$', admin_views.adjustLotIds, name='adjustLotIds'),
    url(r'^admin/printRecordLabels/(?P<auctionId>\d+)/(?P<startingIndex>\d+)/$', admin_views.printRecordLabels, name='printRecordLabels'),
    url(r'^admin/printRecordLabels/(?P<auctionId>\d+)/$', admin_views.printRecordLabels, name='printRecordLabels'),
    url(r'^admin/printLetters/(?P<template>\w+)/(?P<auctionId>\d+)/$', admin_views.printLetters, name='printLetters'),
    url(r'^admin/printLetters/(?P<template>\w+)/$', admin_views.printLetters, name='printLetters'),
    
    url(r'^accounts/passwordChangeDone/$', 
        'django.contrib.auth.views.password_change_done', {'template_name': 'changePasswordDone.html'}),
   
    url(r'^admin/testEmail/$', admin_views.testEmail, name='testEmail'),
   url(r'^admin/test/', admin_views.test, name='test'),

    #for testing and setup only, comment out after done
    url(r'^admin/testInput/(?P<index>\d+)/(?P<length>\d+)/$', admin_views.testItemInput, name='testItemInput'),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^audio/', include('audio.urls')),

    url(r'^$', views.index, name='index'),

    url(r'^(?P<page>.+\.html)$', views.StaticView.as_view()),
    url(r'^bids/$',  TemplateView.as_view(template_name='oldBids.html')),



)

