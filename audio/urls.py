from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout

from audio import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
    url(r'^accounts/login/$',  login),
   	#url(r'^accounts/logout/$', logout),
    (r'^accounts/logout/$', logout,
                          {'next_page': '/audio/accounts/profile'}),
    url(r'^accounts/profile/$', views.profile, name='profile'),
   	url(r'^accounts/register/$', views.register, name='register'),
    url(r'^accounts/contact/$', views.contact_info, name='contact_info'), 
    url(r'^accounts/bids/$', views.bids, name='bids'),
    
    url(r'^catalog/(?P<auctionId>\d+)/(?P<lotId>\d+)$', views.showItem, name='showItem'),
    url(r'^catalog/$', views.catalog, name='catalog'),
 	#url(r'^bidSubmit/$', views.bidSubmit, name='bidSubmit'),
       
)
