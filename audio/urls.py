from django.conf.urls import patterns, url, include
from django.contrib.auth.views import login, logout, password_change, password_change_done
from django.contrib import admin
from audio import views
from audio import admin_views
admin.autodiscover()



urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
    url(r'^accounts/login/$',  login),
    url(r'^accounts/changePassword/$',  password_change, {'template_name': 'changePassword.html'}),
    url(r'^acounts/changePasswordDone/$',
                    password_change_done,
                    name='password_change_done'),
   	#url(r'^accounts/logout/$', logout),
    (r'^accounts/logout/$', logout,
                          {'next_page': '/audio/accounts/profile'}),
    url(r'^accounts/profile/$', views.profile, name='profile'),
   	url(r'^accounts/register/$', views.register, name='register'),
    url(r'^accounts/contact/$', views.contact_info, name='contact_info'), 
    url(r'^accounts/bids/$', views.bids, name='bids'),
    url(r'^accounts/auctionSummary/(?P<auctionId>\d+)$', views.auctionSummary, name='auctionSummary'),
    url(r'^accounts/auctionSummary/$', views.auctionSummaries, name='auctionSummaries'),
    url(r'^accounts/userInfo/$', views.userInfo, name='userInfo'),
    url(r'^catalog/comingAuction/$', views.noAuction, name='noAuction'),
    
    url(r'^catalog/(?P<auctionId>\d+)/(?P<lotId>\d+)$', views.showItem, name='showItem'),
    url(r'^catalog/submitBid', views.submitBid, name='submitBid'),

    url(r'^catalog/simpleForm', views.simpleForm, name='simpleForm'),
    url(r'^catalog/deleteBid', views.deleteBid, name='deleteBid'),
    url(r'^catalog/setPrice', views.flatFeeCatalog, name='flatFeeCatalog'),
    url(r'^catalog/$', views.catalog, name='catalog'),
    url(r'^test', views.test, name='test'),

)





