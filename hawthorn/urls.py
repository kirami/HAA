from django.conf.urls import patterns, include, url

from django.contrib import admin
from audio import views
admin.autodiscover()



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hawthorn.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

	#url(r'^admin/audio/auction/$', report),
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/bookstore/report/$', views.contact_info, name='contact_info'),
    
    url(r'^admin/', include(admin.site.urls)),
	url(r'^audio/', include('audio.urls')),
    #(r'^audio/', include('audio.urls')),
)

