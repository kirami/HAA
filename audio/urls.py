from django.conf.urls import patterns, url, include
from django.contrib.auth.views import login, logout, password_change, password_change_done
from django.contrib import admin
from audio import views
from audio import admin_views
from django.views.generic import TemplateView
admin.autodiscover()



urlpatterns = patterns('',
	url(r'^$', views.audio, name='audio'),
    
    url(r'^accounts/login/$',  login),
    #url(r'^accounts/changePassword/$',  password_change,  {'template_name': 'changePassword.html'}),
    #url(r'^accounts/login/$','django.contrib.auth.views.login',name='login',kwargs={'template_name': 'login.html'}),
    
   

    url(r'^accounts/changePassword/$', 
        'django.contrib.auth.views.password_change', 
      
        {'post_change_redirect' : '/accounts/passwordChangeDone/', 'template_name': 'changePassword.html'}, 

        name="password_change"), 

    

    #url(r'^accounts/logout/$', logout),
    (r'^accounts/logout/$', logout,
                          {'next_page': '/audio/accounts/profile'}),
    url(r'^accounts/settings/$', views.accountSettings, name='accountSettings'),
    url(r'^accounts/profile/$', views.profile, name='profile'),
   	url(r'^accounts/register/$', views.register, name='register'),
    url(r'^accounts/resetPassword/$', views.resetPassword, name='resetPassword'),
    url(r'^accounts/contact/$', views.contact_info, name='contact_info'), 
    url(r'^accounts/bids/$', views.bids, name='bids'),
    url(r'^accounts/verifyEmail/$', views.verifyEmail, name='verifyEmail'),
    url(r'^accounts/auctionSummary/(?P<auctionId>\d+)$', views.auctionSummary, name='auctionSummary'),
    url(r'^accounts/auctionSummary/$', views.auctionSummaries, name='auctionSummaries'),
    url(r'^accounts/userInfo/$', views.userInfo, name='userInfo'),
    url(r'^catalog/comingAuction/$', views.noAuction, name='noAuction'),
    
   # url(r'^catalog/(?P<auctionId>\d+)/(?P<lotId>\d+)$', views.showItem, name='showItem'),
    url(r'^catalog/submitBid', views.submitBid, name='submitBid'),

    url(r'^catalog/simpleForm', views.simpleForm, name='simpleForm'),
    url(r'^catalog/deleteBid', views.deleteBid, name='deleteBid'),
    url(r'^catalog/setPrice', views.flatFeeCatalog, name='flatFeeCatalog'),
    url(r'^catalog/itemInfo/(?P<itemId>\d+)/$', views.itemInfo, name='itemInfo'),
    url(r'^catalog/view/(?P<auctionId>\d+)/$', views.catalog, name='catalog'),
    url(r'^catalog/viewSetSale/(?P<auctionId>\d+)/$', views.flatFeeCatalog, name='flatFeeCatalog'),
    url(r'^catalog/$', views.catalog, name='catalog'),
    url(r'^test', views.test, name='test'),
    url(r'^tom/$',  TemplateView.as_view(template_name='tom.html')),
    url(r'^rules/$',  TemplateView.as_view(template_name='rules.html')),
    url(r'^conditionCodes/$',  TemplateView.as_view(template_name='conditionCodes.html')),
    url(r'^labelAbbreviations/$',  TemplateView.as_view(template_name='labelAbbreviations.html')),
    
    url(r'^accounts/confirm/(?P<confirmation_code>\w+)/(?P<username>\w+)$', views.confirm, name='confirm'),
    url(r'^accounts/confirm/(?P<confirmation_code>\w+)/(?P<username>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.confirm, name='confirm'),

)





