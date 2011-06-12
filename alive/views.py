from alive.models import *
from alive.forms import SortForm
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
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
    try:
        sorting = request.session['sorting']
    except:
        sorting = 'rank'
    try:
        reverse = request.session['reverse']
    except:
        reverse = False
    sortform = SortForm(initial={'type': sorting, 'reverse': reverse})
    ajax = request.GET.has_key('ajax')
    if request.method == 'POST':
        sortform = SortForm(request.POST)
        if sortform.is_valid():
            sorting = sortform.data['type']
            request.session['sorting'] = sortform.data['type']
            try:
                reverse = sortform.data['reverse']
                request.session['reverse'] = True
            except:
                reverse = False
                request.session['reverse'] = False
    taxon = Taxon.objects.select_related().get(slug=slug)
    if reverse:
        articles = taxon.articles.order_by('-' + sorting)
    else:
        articles = taxon.articles.order_by(sorting)
    last_query = Query.objects.filter(taxon=taxon).order_by('-timestamp')[0]
    variables = RequestContext(request, {
        'taxon': taxon,
        'last_query': last_query,
        'articles': articles,
        'sortform': sortform,
        })
    return render_to_response('taxon.html', variables)
