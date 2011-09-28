import json
import os
import sys

from mendeley import mendeley
from datetime import datetime

# Django environment import
from django.core.management import setup_environ
import settings
setup_environ(settings)
from alive.models import *

def get_categories():
    '''Fetch Mendeley category listing.'''
    print 'Checking categories...'
    categories = mendeley.categories()
    for item in categories:
        category, new = Category.objects.get_or_create(name=item['name'], 
                slug=item['slug'], mendeley_id=item['id'])
        if new:
            category.save()
        subcategories = mendeley.subcategories(category.mendeley_id)
        for item in subcategories:
            subcategory, new = Category.objects.get_or_create(name=item['name'], 
                    slug=item['slug'], mendeley_id=item['id'], parent=category, 
                    issub=True)
            if new:
                subcategory.save()
    print 'Done.'

def search(taxon_name, items=50):
    '''Queries Mendeley database for a taxon name.'''
    # Search Mendeley.
    #log 'Searching for %s...' % taxon_name
    # handle connection problems or aborts?
    results = mendeley.search(taxon_name, items=items)

    return results

def fetch(taxon_name):
    '''Queries Mendeley database for a taxon name.'''
    #TODO Urgently create logging, tests and functions here to avoid issues.
    # Create/instantiate taxon.
    taxon, new = Taxon.objects.get_or_create(name=taxon_name)
    if new:
        taxon.save()

    # Search Mendeley.
    print 'Searching for %s...' % taxon_name
    results = mendeley.search(taxon_name, items=50)

    # Create query.
    print 'Creating query...'
    if not results['total_results']:
        results['total_results'] = 0
    query = Query(total_results=results['total_results'], taxon=taxon)
    query.save()

    if results['documents']:
        print 'Getting details...'
        for rank, doc in enumerate(results['documents'], start=1):
            try:
                article = Article.objects.get(uuid=doc['uuid'])
                article.rank = rank
                article.save()
                print 'Article already in the database. Only saving new rank.'
            except:
                details = mendeley.details(doc['uuid'])

                #XXX Make sure an empty detail does not break the script.
                if details:
                    # Store metadata in an object.
                    metadata = {}
                    m2mdata = {}
                    identifiers = {}

                    # Loop over document details.
                    for k, v in details.iteritems():

                        ## ForeignKey
                        # Article type.
                        if k == 'type':
                            type, new = ArticleType.objects.get_or_create(name=v)
                            if new:
                                type.save()
                            metadata['type'] = type

                        # Publication outlet.
                        elif k == 'publication_outlet':
                            journal, new = Journal.objects.get_or_create(name=v)
                            if new:
                                journal.save()
                            metadata['publication_outlet'] = journal

                        # Publisher.
                        elif k == 'publisher':
                            publisher, new = Publisher.objects.get_or_create(name=v)
                            if new:
                                publisher.save()
                            metadata['publisher'] = publisher

                        # Stats.
                        elif k == 'stats':
                            stats = Stats(readers=v['readers'])
                            stats.save()

                            # Country.
                            for item in v['country']:
                                country, new = Country.objects.get_or_create(name=item['name'])
                                if new:
                                    country.save()
                                stats_country = StatsCountry(name=country, value=item['value'])
                                stats_country.save()
                                stats.countries.add(stats_country)

                            # Discipline.
                            for item in v['discipline']:
                                discipline, new = Discipline.objects.get_or_create(name=item['name'])
                                if new:
                                    discipline.save()
                                stats_discipline = StatsDiscipline(name=discipline, 
                                        value=item['value'])
                                stats_discipline.save()
                                stats.disciplines.add(stats_discipline)

                            # Status.
                            for item in v['status']:
                                status, new = Status.objects.get_or_create(name=item['name'])
                                if new:
                                    status.save()
                                stats_status = StatsStatus(name=status, value=item['value'])
                                stats_status.save()
                                stats.statuses.add(stats_status)

                            metadata['stats'] = stats

                        # Many2Many
                        # Authors.
                        elif k == 'authors':
                            m2mdata['authors'] = []
                            for item in v:
                                author, new = Author.objects.get_or_create(
                                        forename=item['forename'], surname=item['surname'])
                                if new:
                                    author.save()
                                m2mdata['authors'].append(author)

                        # Editors.
                        elif k == 'editors':
                            m2mdata['editors'] = []
                            for item in v:
                                editor, new = Editor.objects.get_or_create(
                                        forename=item['forename'], surname=item['surname'])
                                if new:
                                    editor.save()
                                m2mdata['editors'].append(editor)

                        # Categories.
                        #XXX Create categories beforehand.
                        elif k == 'categories':
                            m2mdata['categories'] = []
                            for item in v:
                                category = Category.objects.get(mendeley_id=item, issub=True)
                                m2mdata['categories'].append(category)

                        # Groups.
                        #TODO Create an attribute groups for client...
                        elif k == 'groups':
                            m2mdata['groups'] = []
                            for item in v:
                                #FIXME Transform date in datetime object.
                                group, new = Group.objects.get_or_create(
                                        group_id=item['group_id'])
                                if new:
                                    group.profile_id = item['profile_id']
                                    group.save()
                                m2mdata['groups'].append(group)

                        # Keywords.
                        elif k == 'keywords':
                            m2mdata['keywords'] = []
                            for item in v:
                                keyword, new = Keyword.objects.get_or_create(name=item)
                                if new:
                                    keyword.save()
                                m2mdata['keywords'].append(keyword)

                        # Tags.
                        elif k == 'tags':
                            m2mdata['tags'] = []
                            for item in v:
                                tag, new = Tag.objects.get_or_create(name=item)
                                if new:
                                    tag.save()
                                m2mdata['tags'].append(tag)

                        elif k == 'identifiers':
                            identifiers = v

                        else:
                            # Assert keywords are strings.
                            metadata[str(k)] = v
                            #uuid=details['uuid'],
                            #title=details['title'],
                            #abstract=details['abstract'],
                            #year=details['year'],
                            #volume=details['volume'],
                            #issue=details['issue'],
                            #pages=details['pages'],
                            #website=details['website'],
                            #mendeley_url=details['mendeley_url'],
                            #public_file_hash=details['public_file_hash'],
                            #oa_journal=details['oa_journal']

                    print 'Creating article...'
                    #FIXME Handle "temporarily unavailable" error from Mendeley
                    # {"error":"Mendeley is temporarily unavailable. Please try again later."}
                    article = Article(**metadata)
                    article.rank = rank

                    print 'Saving article...'
                    article.save()
                    print 'Saved!'

                    print 'Adding Many2Many fields...'
                    for k, v in m2mdata.iteritems():
                        if k == 'authors':
                            for item in v:
                                article.authors.add(item)
                        elif k == 'editors':
                            for item in v:
                                article.editors.add(item)
                        elif k == 'categories':
                            for item in v:
                                article.categories.add(item)
                        elif k == 'groups':
                            for item in v:
                                article.groups.add(item)
                        elif k == 'keywords':
                            for item in v:
                                article.keywords.add(item)
                        elif k == 'tags':
                            for item in v:
                                article.tags.add(item)

                    if identifiers:
                        print 'Adding identifiers...'
                        for k, v in identifiers.iteritems():
                            identifier, new = Identifier.objects.get_or_create(type=k, value=v, 
                                    article=article)
                            if new:
                                identifier.save()

                    print 'Adding to taxon...'
                    taxon.articles.add(article)

                    print 'The end.'


# EXEMPLO DE DETAILS:
# {u'abstract': u"Sea biscuits and sand dollars diverged from other irregular 
# echinoids approximately 55 million years ago and rapidly dispersed to oceans 
# worldwide. A series of morphological changes were associated with the 
# occupation of sand beds such as flattening of the body, shortening of primary 
# spines, multiplication of podia, and retention of the lantern of Aristotle 
# into adulthood. To investigate the developmental basis of such morphological 
# changes we documented the ontogeny of Clypeaster subdepressus. We obtained 
# gametes from adult specimens by KCl injection and raised the embryos at 26C. 
# Ciliated blastulae hatched 7.5 h after sperm entry. During gastrulation the 
# archenteron elongated continuously while ectodermal red-pigmented cells 
# migrated synchronously to the apical plate. Pluteus larvae began to feed in 3 
# d and were 20 d old at metamorphosis; starved larvae died 17 d after 
# fertilization. Postlarval juveniles had neither mouth nor anus nor plates on 
# the aboral side, except for the remnants of larval spicules, but their 
# bilateral symmetry became evident after the resorption of larval tissues. 
# Ossicles of the lantern were present and organized in 5 groups. Each group 
# had 1 tooth, 2 demipyramids, and 2 epiphyses with a rotula in between. Early 
# appendages consisted of 15 spines, 15 podia (2 types), and 5 sphaeridia. 
# Podial types were distributed in accordance to Lov n's rule and the first 
# podium of each ambulacrum was not encircled by the skeleton. Seven days after 
# metamorphosis juveniles began to feed by rasping sand grains with the 
# lantern. Juveniles survived in laboratory cultures for 9 months and died with 
# wide, a single open sphaeridium per ambulacrum, aboral anus, and no 
# differentiated food grooves or petaloids. Tracking the morphogenesis of early 
# juveniles is a necessary step to elucidate the developmental mechanisms of 
# echinoid growth and important groundwork to clarify homologies between 
# irregular urchins.",
# u'authors': [{u'forename': u'Bruno C', u'surname': u'Vellutini'},
#              {u'forename': u'Alvaro E', u'surname': u'Migotto'}],
# u'categories': [52, 454, 43, 31, 352, 31],
# u'editors': [{u'forename': u'Christoph', u'surname': u'Winkler'}],
# u'groups': [{u'date_added': 1290733460000L,
#              u'group_id': 693561,
#              u'profile_id': 5060}],
# u'identifiers': {u'doi': u'10.1371/journal.pone.0009654',
#                  u'oai_id': u'oai:pubmedcentral.nih.gov:2842294',
#                  u'other': u'09-PONE-RA-14520R1',
#                  u'pmc_id': u'2842294',
#                  u'pmid': u'20339592'},
# u'issue': u'3',
# u'mendeley_url': u'http://www.mendeley.com/research/embryonic-larval-juvenile-development-sea-biscuit-clypeaster-subdepressus-echinodermata-clypeasteroida/',
# u'oa_journal': True,
# u'pages': u'15',
# u'public_file_hash': u'09f5131d20e2e70d239dbe256e687830b6a9712e',
# u'publication_outlet': u'PLoS ONE',
# u'publisher': u'Public Library of Science',
# u'stats': {u'country': [{u'name': u'Brazil', u'value': 33},
#                         {u'name': u'Australia', u'value': 17},
#                         {u'name': u'', u'value': 17}],
#            u'discipline': [{u'name': u'Biological Sciences', u'value': 83},
#                            {u'name': u'Social Sciences', u'value': 17}],
#            u'readers': 6,
#            u'status': [{u'name': u'Student (Master)', u'value': 33},
#                        {u'name': u'Ph.D. Student', u'value': 33},
#                        {u'name': u'Researcher (at an Academic Institution)',
#                         u'value': 17}]},
# u'title': u'Embryonic, Larval, and Juvenile Development of the Sea Biscuit Clypeaster subdepressus (Echinodermata: Clypeasteroida)',
# u'type': u'Journal Article',
# u'uuid': u'4cf5bde0-6d0d-11df-afb8-0026b95d30b2',
# u'volume': u'5',
# u'website': u'http://www.ncbi.nlm.nih.gov/pubmed/20339592',
# u'year': 2010}

# EXEMPLO DE SEARCHED TERM: "Encope"
#{u'current_page': 0,
# u'documents': [{u'authors': u'Wilson.',
#                 u'doi': None,
#                 u'mendeley_url': u'http://www.mendeley.com/research/study-movement-sand-dollar-encope-grandis/',
#                 u'publication_outlet': None,
#                 u'title': u'A study of Movement by the sand dollar Encope grandis',
#                 u'uuid': u'cf79b150-d84b-11df-82d0-0024e8453de6',
#                 u'year': 1966},
#                {u'authors': u'I et al.',
#                 u'doi': u'10.1017/S002531540400935Xh',
#                 u'mendeley_url': u'http://www.mendeley.com/research/vertical-posture-of-the-clypeasteroid-sand-dollar-encope-michelini/',
#                 u'publication_outlet': u'Journal of the Marine Biological Association of the UK',
#                 u'title': u'Vertical posture of the clypeasteroid sand dollar Encope michelini',
#                 u'uuid': u'2199f220-6d07-11df-afb8-0026b95d30b2',
#                 u'year': 2004},
#                {u'authors': u'Burns.',
#                 u'doi': None,
#                 u'mendeley_url': u'http://www.mendeley.com/research/study-niche-separation-convergent-evolution-two-species-sand-dollars-encope-microspora-encope-grandis/',
#                 u'publication_outlet': None,
#                 u'title': u'A study of Niche separation and convergent evolution in two species of sand dollars, Encope microspora and Encope grandis',
#                 u'uuid': u'b2798760-d84b-11df-82d0-0024e8453de6',
#                 u'year': 1966},
#                {u'authors': u'Meier.',
#                 u'doi': None,
#                 u'mendeley_url': u'http://www.mendeley.com/research/relationship-sand-dollar-encope-grandis-coexhisting-crab/',
#                 u'publication_outlet': None,
#                 u'title': u'Relationship of the Sand Dollar Encope grandis and a co-exhisting Crab',
#                 u'uuid': u'bc61b130-d84b-11df-82d0-0024e8453de6',
#                 u'year': 1978},
#                {u'authors': u'Dexter.',
#                 u'doi': None,
#                 u'mendeley_url': u'http://www.mendeley.com/research/natural-history-sand-dollar-encope-stokesi-l-agassiz-panama/',
#                 u'publication_outlet': None,
#                 u'title': u'A natural history of the sand dollar Encope stokesi L. Agassiz in Panama',
#                 u'uuid': u'53cc1b30-6d0a-11df-afb8-0026b95d30b2',
#                 u'year': 1977},
#                {u'authors': u'Dexter.',
#                 u'doi': None,
#                 u'mendeley_url': u'http://www.mendeley.com/research/natural-history-sand-dollar-encope-l-agassiz-panama/',
#                 u'publication_outlet': None,
#                 u'title': u'A NATURAL HISTORY OF THE SAND DOLLAR ENCOPE L . AGASSIZ IN PANAMA',
#                 u'uuid': u'577db630-0323-11e0-95f0-0024e8453de6',
#                 u'year': 1977},
#                {u'authors': u'Lawrence et al.',
#                 u'doi': None,
#                 u'mendeley_url': u'http://www.mendeley.com/research/bilateral-symmetry-petals-mellita-tenuis-encope-micropora-arachnoides-placenta-echinodermata-clypeasteroida/',
#                 u'publication_outlet': None,
#                 u'title': u'Bilateral symmetry of the petals in Mellita tenuis, Encope micropora, and Arachnoides placenta (Echinodermata : Clypeasteroida)',
#                 u'uuid': u'0a86faa0-39ef-11e0-babf-0024e8453de6',
#                 u'year': 1998},
#                {u'authors': u'Reichholf.',
#                 u'doi': None,
#                 u'mendeley_url': u'http://www.mendeley.com/research/some-data-sample-sanddollar-encope-emarginata-leske-1778-coast-santa-catarina-brazil/',
#                 u'publication_outlet': u'Spixiana',
#                 u'title': u'Some Data on a Sample of the Sanddollar Encope emarginata (Leske, 1778) from the Coast of Santa Catarina, Brazil',
#                 u'uuid': u'75db3630-ddd4-11df-874c-0024e8453de6',
#                 u'year': 1981},
#                {u'authors': u'Eckert.',
#                 u'doi': None,
#                 u'mendeley_url': u'http://www.mendeley.com/research/a-novel-larval-feeding-strategy-of-the-tropical-sand-dollar-encope-michelini-agassiz-adaptation-to-food-limitation-and-an-evolutionary-link-between-planktotrophy-and-lecithotrophy-1/',
#                 u'publication_outlet': u'Journal of Experimental Marine Biology and Ecology',
#                 u'title': u'A novel larval feeding strategy of the tropical sand dollar Encope michelini (Agassiz): adaptation to food limitation and an evolutionary link between planktotrophy and lecithotrophy',
#                 u'uuid': u'1c1e9850-6d07-11df-afb8-0026b95d30b2',
#                 u'year': 1995},
#                {u'authors': u'Ebert, Dexter.',
#                 u'doi': None,
#                 u'mendeley_url': u'http://www.mendeley.com/research/naturalhistory-study-encopegrandis-mellitagrantii-2-sand-dollars-northern-gulf-california-mexico/',
#                 u'publication_outlet': u'Marine Biology',
#                 u'title': u'Natural-History Study of Encope-Grandis and Mellita-Grantii, 2 Sand Dollars in Northern Gulf of California, Mexico',
#                 u'uuid': u'20b08e70-6d05-11df-afb8-0026b95d30b2',
#                 u'year': 1975}],
# u'items_per_page': u'10',
# u'total_pages': 2,
# u'total_results': 17}

