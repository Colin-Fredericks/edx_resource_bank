# from django.http import HttpResponse
# from django.template import RequestContext, loader

from django.http import Http404
from django.shortcuts import render
from RDB.models import Resource, Analytic_Value

# def index(request):
#	 latest_resource_list = Resource.objects.order_by('-creation_date')[:5]
#	 output = ', '.join([p.name for p in latest_resource_list])
#	 polished_output = '<p>Here is a list of recent resources in creation-date order:</p>' + '<p>' + output + '</p>'
#	 return HttpResponse(polished_output)


def index(request):
	resource_list = Resource.objects.all().order_by('id')
	latest_resource_list = Resource.objects.all().order_by('-creation_date')[:5]
	context = {
		'latest_resource_list': latest_resource_list, 
		'resource_list': resource_list,	
	}
	return render(request,'RDB/index.html',context)


def detail(request, resource_id):
	try:
		res = Resource.objects.get(pk=resource_id)
	except Resource.DoesNotExist:
		raise Http404
	analytic_values = Analytic_Value.objects.filter(resource=res)
	return render(request, 'RDB/detail.html', {'resource': res, 'analytic_values': analytic_values,})


def results(request, resource_id):
	return HttpResponse("You're seeing changes of results in resource #%s." % resource_id)

def vote(request, resource_id):
	return HttpResponse("You're changing resource #%s." % resource_id)