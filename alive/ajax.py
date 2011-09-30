# -*- coding: utf-8 -*-
from alive.models import Article, Query, Taxon, UserProfile
from alive.views import get_ratio, get_yearly
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from django.template.defaultfilters import date
from django.conf.global_settings import DATETIME_FORMAT
from runalive import details, search


@dajaxice_register
def search_references(request, taxon_id):
    '''Search references related to the taxon using Mendeley.'''
    dajax = Dajax()

    #items = items_per_page + items_per_page
    items = 50

    # Get taxon.
    taxon = Taxon.objects.get(id=taxon_id)

    # Search Mendeley.
    results = search(taxon.name, items=items)

    # Create database query.
    if not results['total_results']:
        results['total_results'] = 0
    query = Query(total_results=results['total_results'], taxon=taxon)
    query.save()

    # Define values.
    articles_count = taxon.articles.count()
    total_results = results['total_results']

    # Get ratio.
    fetch_ratio = get_ratio(articles_count, total_results)

    # Extract only uuid from documents.
    uuids = [str(document['uuid']) for document in results['documents']]

    # Get datetime object.
    timestamp = query.timestamp

    # Assign values to be updated.
    #TODO Format timestamp appropriately.
    dajax.assign('#last-updated', 'innerHTML', date(timestamp, DATETIME_FORMAT))
    dajax.assign('#fetch-ratio', 'innerHTML', fetch_ratio)
    dajax.assign('#total-results', 'innerHTML', total_results)
    dajax.script('$("#updating").fadeOut();')
    dajax.script('$("#fetching-notice").fadeIn();')
    dajax.script('$("#fetching-notice #yellow-loading").fadeIn();')
    dajax.assign('#being-fetched', 'innerHTML', items)
    dajax.script('Dajaxice.livingbib.alive.get_details(Dajax.process, {"uuids": "%s", "articles_count": "%d", "total_results": "%d", "rank": "0", "new": "0", "taxon_id": "%s"})' % (uuids, articles_count, total_results, taxon_id))
    return dajax.json()

@dajaxice_register
def get_details(request, uuids, articles_count, total_results, rank, new, taxon_id):
    '''Extract details from each reference using Mendeley.'''
    dajax = Dajax()

    # Default value to identify duplicates.
    duplicate = False

    # Convert string response to list. #XXX be careful...
    uuids = eval(uuids)
    # Convert to integer.
    articles_count = int(articles_count)
    total_results = int(total_results)
    # Update ranking value.
    rank = int(rank)
    rank += 1
    # Update new value.
    new = int(new)

    # Make sure object is a list.
    if isinstance(uuids, list):
        items = len(uuids)
    else:
        logger.debug('Something is wrong, not a list.')
        #TODO Make dialog about this error...
        #dajax.assign('#being-fetched', 'innerHTML', 'ERROR')
        return dajax.json()

    # Captura o primeiro artigo da lista.
    try:
        uuid = uuids.pop(0)
    except IndexError:
        dajax.script('$("#fetching-status").fadeOut();')
        dajax.remove_css_class('#fetching-notice', 'warning')
        dajax.add_css_class('#fetching-notice', 'success')
        if new == 0:
            dajax.assign('#fetching-notice p', 'innerHTML', 'Success! Database is up-to-date, no new references.')
        else:
            dajax.assign('#fetching-notice p', 'innerHTML', 'Success! Imported %d new references, have fun.' % new)
        dajax.script('$("#fetching-notice").delay(5000).fadeOut("slow");')
        return dajax.json()

    # Get details from Mendeley.
    try:
        article = Article.objects.get(uuid=uuid)
        #article.rank = rank
        #article.save()
        duplicate = True
    except:
        article = details(uuid, rank, taxon_id)
        if article:
            articles_count += 1
            new += 1

    # Get article title.
    try:
        title = article.title
    except:
        title = 'Empty title...'

    # Recalculate the fetch ratio.
    fetch_ratio = get_ratio(articles_count, total_results)

    # Create row #TODO create separate function.
    if not duplicate and article:
        authors = ', '.join(['%s %s' % (author.surname, author.forename) for author in article.authors.all()])

        journal = '<em>%s</em>, %s' % (article.publication_outlet, article.volume)

        if article.issue:
            journal = journal + '(%s)' % article.issue
        journal = journal + ', %sp' % article.pages
        if article.chapter:
            journal = journal + ', %s' % article.chapter

        fields = [
                article.year,
                article.title,
                authors,
                journal,
                article.type,
                article.stats.readers,
                ]

        columns = '["%s","%s","%s","%s","%s","%s"]' % (article.year, article.title, authors, journal, article.type, article.stats.readers)

        row = '$("#references-table").dataTable().fnAddData(%s);' % columns
        dajax.script(row)

    # Update annual graph.
    taxon = Taxon.objects.get(id=taxon_id)
    articles = taxon.articles.all()
    data = get_yearly(articles)

    # Assign values to be updated.
    dajax.script('$("#fetching-status").fadeIn();')
    if duplicate:
        dajax.assign('#fetching-status', 'innerHTML', '<span class="label notice">duplicate</span> %s' % title)
    else:
        dajax.assign('#fetching-status', 'innerHTML', '<span class="label success">new</span> %s' % title)
    dajax.assign('#fetch-ratio', 'innerHTML', fetch_ratio)
    dajax.assign('#being-fetched', 'innerHTML', items)
    dajax.assign('.spark', 'title', "Number of references per year from %d to %d" % (data['min'], data['max']))
    dajax.script('$(".spark").sparkline(%s, {"width": "460px"});' % data['values'])
    dajax.script('Dajaxice.livingbib.alive.get_details(Dajax.process, {"uuids": "%s", "articles_count": "%d", "total_results": "%d", "rank": "%d", "new": "%d", "taxon_id": "%s"});' % (uuids, articles_count, total_results, rank, new, taxon_id))
    return dajax.json()

@dajaxice_register
def toggle_follow(request, taxon_id, user_id):
    '''Search references related to the taxon using Mendeley.'''
    dajax = Dajax()

    # Get user.
    user = UserProfile.objects.get(user__id=user_id)
    taxa_ids = user.taxa.values_list('id', flat=True)

    # Get taxon.
    taxon = Taxon.objects.get(id=taxon_id)

    # Check if taxon is being followed.
    if int(taxon_id) in taxa_ids:
        user.taxa.remove(taxon)
        dajax.remove_css_class('#follow-button', 'success')
        dajax.add_css_class('#follow-button', 'info')
        dajax.assign('#follow-button', 'value', 'Follow')
    else:
        user.taxa.add(taxon)
        dajax.remove_css_class('#follow-button', 'info')
        dajax.add_css_class('#follow-button', 'success')
        dajax.assign('#follow-button', 'value', 'Following')

    return dajax.json()
