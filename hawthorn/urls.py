from django.conf.urls import patterns, include, url

from django.contrib import admin
from audio import views
from audio import admin_views
admin.autodiscover()



urlpatterns = patterns('',

    #url(r'^blog/', include('blog.urls')),
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/bookstore/report/$', admin_views.test, name='test'),
    url(r'^admin/report/$', admin_views.runReport, name='runReport'),
    url(r'^admin/markWinners/$', admin_views.markWinners, name='markWinners'),
    url(r'^admin/winners/$', admin_views.winners, name='winners'),
    url(r'^admin/losers/$', admin_views.losers, name='losers'),
    url(r'^admin/wonItems/$', admin_views.wonItems, name='wonItems'),
    url(r'^admin/unsoldItems/$', admin_views.unsoldItems, name='unsoldItems'), 
    url(r'^admin/bulkConsignment/$', admin_views.bulkConsignment, name='bulkConsignment'),
    url(r'^admin/balances/(?P<userId>\d+)', admin_views.userBalanceInfo, name='userBalanceInfo'),     
    url(r'^admin/balances/$', admin_views.calculateBalances, name='calculateBalances'),

    url(r'^admin/consignorReport/(?P<consignorId>\d+)', admin_views.consignorReportById, name='consignorReportById'),   
    url(r'^admin/consignorReport/$', admin_views.consignorReport, name='consignorReport'),   
    url(r'^admin/', include(admin.site.urls)),
	url(r'^audio/', include('audio.urls')),

)

