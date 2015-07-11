from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^reg_query/$', 'registry.views.reg_query', name='reg_query'),
    url(r'^reg_connect/$', 'registry.views.reg_connect'),
    url(r'^reg_remove/$', 'registry.views.reg_remove'),
    url(r'^reg/$', 'registry.views.reg'),
    url(r'^regp/$', 'registry.views.regp'),
    url(r'^reg_config/$', 'registry.views.reg_config'),
)

