from django.conf.urls import patterns, url

from audio import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)