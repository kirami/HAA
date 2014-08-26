from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response

from django.template import RequestContext, loader

def index(request):
	t = loader.get_template('home.html')
	c = RequestContext(request, {'foo': 'bar'})
	return HttpResponse(t.render(c), content_type="application/xhtml+xml")
# Create your views here.
