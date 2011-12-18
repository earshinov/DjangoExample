# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', redirect_to, { 'url': '/field-list/' }),
    (r'^field-list/$', 'fields.views.fieldList'),
    (r'^field-editor/$', 'fields.views.fieldEditor'),
    (r'^switch-language/$', 'language_selection.views.switchLanguage'),
    (r'^i18n/', include('django.conf.urls.i18n')),

    # Examples:
    # url(r'^$', 'AdditionalFields.views.home', name='home'),
    # url(r'^AdditionalFields/', include('AdditionalFields.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
