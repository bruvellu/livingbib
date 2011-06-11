from alive.models import *
#from alive.forms import *
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
#from django.core.paginator import Paginator, InvalidPage, EmptyPage
#from django.contrib.auth.decorators import login_required
#from django.core.cache import cache

def home_page(request):
    '''Home page.'''
    taxa = Taxon.objects.select_related()
    variables = RequestContext(request, {
        'taxa': taxa,
        })
    return render_to_response('home.html', variables)

def taxon_page(request, slug):
    '''Taxon page.'''
    taxon = Taxon.objects.select_related().get(slug=slug)
    last_query = Query.objects.filter(taxon=taxon).order_by('-timestamp')[0]
    variables = RequestContext(request, {
        'taxon': taxon,
        'last_query': last_query,
        })
    return render_to_response('taxon.html', variables)
