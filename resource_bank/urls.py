from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from RDB import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'MechRevTest.views.home', name='home'),
    # url(r'^MechRevTest/', include('MechRevTest.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^RDB/', include('RDB.urls')),

)
