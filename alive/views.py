from commands import *
from models import *
from forms import *
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from livingbib.ubio import uBio
import pickle
from datetime import datetime, timedelta
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
            try:
                # Queries are cached as pickle objects.
                taxapic = open('queries/' + query, 'rb')
                taxa = pickle.load(taxapic)
                taxapic.close()
            except:
                #TODO Handle connection problems, better at ubio.py.
                ubio = uBio()
                taxa = ubio.search_name(query)
                taxapic = open('queries/' + query, 'wb')
                pickle.dump(taxa, taxapic)
                taxapic.close()
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
        # Pretend it is a regular query.
        query = slug.replace('-', ' ')
        # Call uBio to help.
        ubio = uBio()
        taxa = ubio.search_name(query)
        # Uppercase the first letter of the first word.
        prename = query.split(' ')
        prename[0] = prename[0].title()
        name = ' '.join(prename)
        # Scan query results to check if the slug (taxon) exists.
        # It must be an exact match to a known uBio entry to create the taxon.
        for entry in taxa:
            if entry['name'].lower() == query.lower():
                taxon = Taxon(name=name)
                taxon.save()
        #XXX What happens when taxon object is not created?

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

    # Calls for reference fetching.
    fetching = False
    if not last_query:
        fetch_references(taxon.name) # New taxon.
        fetching = True
    else:
        now = datetime.now()
        if (now - last_query.timestamp) > timedelta(days=7):
            fetch_references(taxon.name) # Checks again for updates.
            fetching = True

    variables = RequestContext(request, {
        'taxon': taxon,
        'last_query': last_query,
        'articles': articles,
        'sortform': sortform,
        'top_authors': top_authors,
        'fetching': fetching,
        })
    return render_to_response('taxon.html', variables)
