from django.conf.urls import patterns, url

from RDB import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),


	# ex: /RDB/
	url(r'^$', views.index, name='index'),
	# ex: /RDB/5/
	url(r'^(?P<resource_id>\d+)/$', views.detail, name='detail'),
	# ex: /RDB/collection/5/
	url(r'^collection/(?P<collection_id>\d+)/$', views.collection, name='collection'),
	
#	# ex: /RDB/5/results/
#	url(r'^(?P<resource_id>\d+)/results/$', views.results, name='results'),
#	# ex: /RDB/5/vote/
#	url(r'^(?P<resource_id>\d+)/vote/$', views.vote, name='vote'),

)