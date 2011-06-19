from models import *
from forms import *
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from ubio import uBio
#from django.core.paginator import Paginator, InvalidPage, EmptyPage
#from django.contrib.auth.decorators import login_required
#from django.core.cache import cache

def home_page(request):
    '''Home page.'''
    taxa = Taxon.objects.select_related().order_by('-total_results')
    form = SearchForm()
    variables = RequestContext(request, {
        'taxa': taxa,
        'form': form,
        })
    return render_to_response('home.html', variables)

def search_page(request):
    '''Search page.'''
    form = SearchForm()
    taxa = []
    query = ''
    scientific, vernacular = [], []
    show = False
    if 'query' in request.GET:
        query = request.GET['query'].strip()
        if query:
            form = SearchForm({'query': query})
            show = True
            ubio = uBio()
            taxa = ubio.search_name(query)
    variables = RequestContext(request, {
        'form': form,
        'query': query,
        'show': show,
        'taxa': taxa,
        })
    return render_to_response('search.html', variables)

def taxon_page(request, slug):
    '''Taxon page.'''

    # Handling session keys for sorting.
    try:
        sorting = request.session['sorting']
    except:
        sorting = 'rank'
    try:
        reverse = request.session['reverse']
    except:
        reverse = False

    # Handling search form.
    sortform = SortForm(initial={'type': sorting, 'reverse': reverse})
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

    # Get or create taxon instance.
    try:
        taxon = Taxon.objects.select_related().get(slug=slug)
    except:
        query = slug.replace('-', ' ')
        ubio = uBio()
        taxa = ubio.search_name(query)
        prename = query.split(' ')
        prename[0] = prename[0].title()
        name = ' '.join(prename)
        for entry in taxa:
            if entry['name'].lower() == query.lower():
                taxon = Taxon(name=name)
                taxon.save()

    # Deal with articles.
    if reverse:
        articles = taxon.articles.order_by('-' + sorting)
    else:
        articles = taxon.articles.order_by(sorting)

    try:
        last_query = Query.objects.filter(taxon=taxon).order_by('-timestamp')[0]
    except:
        last_query = ''

    try:
        top_authors = articles.values('authors__forename', 'authors__surname').annotate(Count('authors')).order_by('-authors__count')[:10]
    except:
        top_authors = []
    variables = RequestContext(request, {
        'taxon': taxon,
        'last_query': last_query,
        'articles': articles,
        'sortform': sortform,
        'top_authors': top_authors,
        })
    return render_to_response('taxon.html', variables)
