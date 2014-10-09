from django.conf.urls import patterns, include, url

from django.contrib import admin
from audio import views
from audio import admin_views
admin.autodiscover()



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hawthorn.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

	#url(r'^admin/audio/auction/$', report),
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/bookstore/report/$', admin_views.test, name='test'),
    url(r'^admin/report/$', admin_views.runReport, name='runReport'),
    url(r'^admin/markWinners/$', admin_views.markWinners, name='markWinners'),
    
    url(r'^admin/', include(admin.site.urls)),
	url(r'^audio/', include('audio.urls')),
    #(r'^audio/', include('audio.urls')),
)

