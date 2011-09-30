from commands import *
from models import *
from forms import *
from django.db.models import Avg, Count, Max, Min
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

#XXX Calling topbar search form in every view...
# Might be better to create a template tag, but need some work to handle requests.

def home_page(request):
    '''Home page.'''
    # Search form.
    form = SearchForm()
    taxa = Taxon.objects.select_related().order_by('-total_results')[:15]
    queries = Query.objects.select_related().order_by('-timestamp')
    variables = RequestContext(request, {
        'taxa': taxa,
        'form': form,
        'queries': queries,
        })
    return render_to_response('home.html', variables)

def search_page(request):
    '''Search page.'''
    # Search form.
    form = SearchForm()

    # Default values for objects.
    taxa = []
    query = ''
    scientific, vernacular = [], []
    show = False

    if 'query' in request.GET:
        query = clean_query(request.GET['query'])
        if query:
            # Flag to show results in the template.
            show = True

            # Get taxa from pickled objects or via uBio.
            taxa = query_handler(query)

    variables = RequestContext(request, {
        'form': form,
        'query': query,
        'show': show,
        'taxa': taxa,
        'n': len(taxa),
        })
    if request.is_ajax():
        return render_to_response('search_results.html', variables)
    else:
        return render_to_response('search.html', variables)

def taxon_page(request, slug):
    '''Taxon page.'''
    # Search form.
    form = SearchForm()

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
        words = query.split(' ')
        words[0] = words[0].title()
        name = ' '.join(words)
        # Scan query results to check if the slug (taxon) exists.
        # It must be an exact match to a known uBio entry to create the taxon.
        for entry in taxa:
            if entry['name'].lower() == query.lower():
                taxon = Taxon(name=name)
                taxon.save()
            else:
                #XXX What happens when taxon object is not created?
                pass

    # Get all related articles.
    articles = taxon.articles.all()

    # Check if a query object was created recently.
    try:
        last_query = Query.objects.filter(taxon=taxon).order_by('-timestamp')[0]
    except:
        last_query = ''

    # Top ten authors in number of publications with the taxon.
    #TODO Explore possibilities.
    try:
        top_authors = articles.values('authors__forename', 'authors__surname').annotate(Count('authors')).order_by('-authors__count')[:10]
    except:
        top_authors = []

    # Number of publications per year.
    if articles:
        data = get_yearly(articles)
    else:
        data = {}

    # Calls for reference fetching.
    fetching = False
    if not last_query:
        #fetch_references(taxon.name) # New taxon.
        fetching = True
    else:
        now = datetime.now()
        if (now - last_query.timestamp) > timedelta(days=1):
            #fetch_references(taxon.name) # Checks again for updates.
            fetching = True

    # Calculate the ratio of existent and fetched articles.
    if last_query:
        fetch_ratio = get_ratio(articles.count(), last_query.total_results)
    else:
        fetch_ratio = 0

    user_list = taxon.taxon_users.values_list('id', flat=True)

    variables = RequestContext(request, {
        'taxon': taxon,
        'last_query': last_query,
        'articles': articles,
        'top_authors': top_authors,
        'fetching': fetching,
        'fetch_ratio': fetch_ratio,
        'form': form,
        'user_list': user_list,
        'data': data,
        })
    return render_to_response('taxon.html', variables)

def user_page(request, slug):
    '''User page.'''
    # Search form.
    form = SearchForm()

    # Get user.
    user_profile = get_object_or_404(UserProfile, slug=slug)

    # Get username.
    username = user_profile.user.username

    # Get followed taxa.
    taxa = user_profile.taxa.all()

    variables = RequestContext(request, {
        'user_profile': user_profile,
        'username': username,
        'taxa': taxa,
        'form': form,
        })
    return render_to_response('user.html', variables)

def get_ratio(articles_count, total_results):
    '''Return the ratio between number of articles and total_results.'''
    #FIXME Database can have more articles than what Mendeley has...
    if total_results != 0:
        fetch_ratio = articles_count / float(total_results) * 100
        fetch_ratio = round(fetch_ratio, 2)
    else:
        fetch_ratio = 0
    return fetch_ratio

def get_yearly(articles):
    '''Return number of publications per year.'''
    # Counts per year.
    yearly = articles.values('year').annotate(count=Count('year'))
    # Latest year.
    latest = articles.aggregate(Max('year'))
    latest = latest['year__max']
    # Earliest year.
    earliest = articles.aggregate(Min('year'))
    earliest = earliest['year__min']

    # Full data dictionary.
    years = {}

    # Fill years with empty values.
    for year in range(earliest, latest + 1):
        years[year] = 0
    # Get results and overwrite data dictionary.
    for y in yearly:
        years[y['year']] = y['count']

    data = {
            'values': [],
            'labels': [],
            'max': latest,
            'min': earliest,
            'mean': 0,
            }

    keys = years.keys()
    keys.sort()

    for k in keys:
        data['values'].append(years[k])
        data['labels'].append(k)

    return data

def clean_query(query):
    '''Remove exceding white space and force lowercase.'''
    cleaned_query = query.strip().lower()
    return cleaned_query

def query_handler(query):
    '''Manage query and return taxa from uBio.'''
    # Get taxa from pickled objects or via uBio.
    try:
        # Queries are cached as pickled objects.
        taxapic = open('queries/' + query, 'rb')
        taxa = pickle.load(taxapic)
        taxapic.close()
    except:
        #TODO Handle connection problems, better at ubio.py.
        ubio = uBio()
        taxa = ubio.search_name(query)

        # Save query as pickled object.
        taxapic = open('queries/' + query, 'wb')
        pickle.dump(taxa, taxapic)
        taxapic.close()
    return taxa
