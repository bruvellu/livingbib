from django.db import models
from django.utils.translation import ugettext_lazy as _

from signals import *


class Query(models.Model):
    '''Search term (=taxon name) sent to Mendeley API.'''
    total_results = models.PositiveIntegerField(_('number of results'), default=0)
    #items_per_page = models.PositiveIntegerField(_('fetched items'), default=0)
    timestamp = models.DateTimeField(_('datetime of query'), auto_now_add=True)
    taxon = models.ForeignKey('Taxon', verbose_name=_('taxon'))
    delta = models.IntegerField(null=True, blank=True)


class Taxon(models.Model):
    '''Represents a taxon.'''
    name = models.CharField(_('name'), max_length=256, unique=True)
    rank = models.CharField(_('rank'), max_length=256, blank=True)
    slug = models.SlugField(_('slug'), max_length=256, blank=True)
    tsn = models.PositiveIntegerField(null=True, blank=True)
    aphia = models.PositiveIntegerField(null=True, blank=True)
    total_results = models.PositiveIntegerField(null=True, blank=True)
    delta = models.IntegerField(null=True, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, 
            related_name='children', verbose_name=_('parent'))
    queries = models.ManyToManyField(Query, null=True, blank=True, 
            verbose_name=_('queries'), related_name='taxa')
    articles = models.ManyToManyField('Article', null=True, blank=True, 
            verbose_name=_('articles'), related_name='taxa')

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.rank)

    @models.permalink
    def get_absolute_url(self):
        return ('taxon_url', [self.slug])


class Author(models.Model):
    '''Represents an author.'''
    forename = models.CharField(_('forename'), max_length=256)
    surname = models.CharField(_('surname'), max_length=256)

    def __unicode__(self):
        return '%s %s' % (self.forename, self.surname)


class Editor(models.Model):
    '''Represents an editor.'''
    forename = models.CharField(_('forename'), max_length=256)
    surname = models.CharField(_('surname'), max_length=256)

    def __unicode__(self):
        return '%s %s' % (self.forename, self.surname)


class Category(models.Model):
    '''Represents a Mendeley category.'''
    name = models.CharField(_('name'), max_length=256)
    slug = models.SlugField(_('slug'), max_length=256)
    mendeley_id = models.PositiveIntegerField(_('mendeley_id'), default=0)
    parent = models.ForeignKey('self', blank=True, null=True, 
            related_name='subcategories', verbose_name=_('parent'))
    issub = models.BooleanField(_('is subcategory'), default=False)

    def __unicode__(self):
        return self.name


class Group(models.Model):
    '''Represents a Mendeley group.'''
    #name = models.CharField(_('name'), max_length=256, unique=True)
    #date_added = models.DateTimeField(_('date_added'))
    group_id = models.PositiveIntegerField(_('group_id'), default=0, 
            primary_key=True)
    profile_id = models.PositiveIntegerField(_('profile_id'), default=0)


class Keyword(models.Model):
    '''Represents a Mendeley keyword.'''
    name = models.CharField(_('name'), max_length=256, unique=True)

    def __unicode__(self):
        return self.name


class Tag(models.Model):
    '''Represents a Mendeley tag.'''
    name = models.CharField(_('name'), max_length=256, unique=True)

    def __unicode__(self):
        return self.name


class ArticleType(models.Model):
    '''Type of article (eg, journal Article, PhD Thesis, etc).'''
    name = models.CharField(_('name'), max_length=256, unique=True)

    def __unicode__(self):
        return self.name


class Journal(models.Model):
    '''Scientific journal or other publication outlet.'''
    name = models.CharField(_('name'), max_length=256, unique=True)

    def __unicode__(self):
        return self.name


class Publisher(models.Model):
    '''Represents the publisher.'''
    name = models.CharField(_('name'), max_length=256, unique=True)

    def __unicode__(self):
        return self.name


class Country(models.Model):
    '''Represents a country.'''
    name = models.CharField(_('name'), max_length=256, unique=True)

    def __unicode__(self):
        return self.name


class Discipline(models.Model):
    '''Represents a discipline.'''
    name = models.CharField(_('name'), max_length=256, unique=True)

    def __unicode__(self):
        return self.name


class Status(models.Model):
    '''Represents a status.'''
    name = models.CharField(_('name'), max_length=256, unique=True)

    def __unicode__(self):
        return self.name


class StatsCountry(models.Model):
    '''Represents the stats of countries.'''
    name = models.ForeignKey(Country, verbose_name=_('country'))
    value = models.PositiveIntegerField(_('value'), default=0)

    def __unicode__(self):
        return '%s %s' % (self.name, self.value)


class StatsDiscipline(models.Model):
    '''Represents the stats of disciplines.'''
    name = models.ForeignKey(Discipline, verbose_name=_('discipline'))
    value = models.PositiveIntegerField(_('value'), default=0)

    def __unicode__(self):
        return '%s %s' % (self.name, self.value)


class StatsStatus(models.Model):
    '''Represents the stats of status.'''
    name = models.ForeignKey(Status, verbose_name=_('status'))
    value = models.PositiveIntegerField(_('value'), default=0)

    def __unicode__(self):
        return '%s %s' % (self.name, self.value)


class Stats(models.Model):
    '''An aggregation of stats related to a query.'''
    readers = models.PositiveIntegerField(_('readers'), default=0)
    countries = models.ManyToManyField(StatsCountry, null=True, blank=True, 
            verbose_name=_('countries'))
    disciplines = models.ManyToManyField(StatsDiscipline, null=True, 
            blank=True, verbose_name=_('disciplines'))
    statuses = models.ManyToManyField(StatsStatus, null=True, blank=True, 
            verbose_name=_('status'))

    def __unicode__(self):
        return self.readers + ' readers id=' + self.id


class Article(models.Model):
    '''A bibliographical reference.'''
    # Char
    uuid = models.CharField(_('uuid'), max_length=256, unique=True)
    title = models.CharField(_('title'), max_length=256)
    abstract = models.TextField(_('abstract'), blank=True)
    year = models.PositiveIntegerField(_('year'), default=0)
    rank = models.PositiveIntegerField(_('rank'), default=0)
    chapter = models.CharField(_('chapter'), max_length=10)
    volume = models.CharField(_('volume'), max_length=10)
    issue = models.CharField(_('issue'), max_length=10)
    pages = models.CharField(_('pages'), max_length=50)
    website = models.CharField(_('website'), max_length=256)
    mendeley_url = models.CharField(_('mendeley_url'), max_length=256)
    public_file_hash = models.CharField(_('public_file_hash'), max_length=256)
    # Bool
    oa_journal = models.BooleanField(_('oa_jornal'), default=False)
    # ForeignKey
    type = models.ForeignKey(ArticleType, null=True, blank=True, 
            verbose_name=_('type'))
    publication_outlet = models.ForeignKey(Journal, null=True, blank=True, 
            verbose_name=_('journal'))
    publisher = models.ForeignKey(Publisher, null=True, blank=True, 
            verbose_name=_('publisher'))
    stats = models.ForeignKey(Stats, null=True, blank=True, 
            verbose_name=_('stats'))
    # ManyToMany
    authors = models.ManyToManyField(Author, null=True, blank=True, 
            verbose_name=_('authors'))
    editors = models.ManyToManyField(Editor, null=True, blank=True, 
            verbose_name=_('editors'))
    categories = models.ManyToManyField(Category, null=True, blank=True, 
            verbose_name=_('categories'))
    groups = models.ManyToManyField(Group, null=True, blank=True, 
            verbose_name=_('groups'))
    keywords = models.ManyToManyField(Keyword, null=True, blank=True, 
            verbose_name=_('keywords'))
    tags = models.ManyToManyField(Tag, null=True, blank=True, 
            verbose_name=_('tags'))

    def __unicode__(self):
        return '%s %s' % (self.year, self.title)


class Identifier(models.Model):
    '''Identifiers for an article.'''
    article = models.ForeignKey(Article, verbose_name=_('article'))
    type = models.CharField(_('type'), max_length=256)
    value = models.CharField(_('value'), max_length=256)

    def __unicode__(self):
        return self.type + ': ' + self.value

    def get_absolute_url(self):
        if self.type == 'doi':
            return 'http://dx.doi.org/%s' % self.value
        elif self.type == 'pmid':
            return 'http://www.ncbi.nlm.nih.gov/pubmed/%s' % self.value
        elif self.type == 'pmc_id':
            return 'http://www.ncbi.nlm.nih.gov/pmc/articles/PMC%s/' % self.value
        else:
            return None
        #elif self.type == 'issn':
        #    return 'http://www.google.com/search?tbm=bks&q=issn:%s' % self.value


# Signals calls.
signals.pre_save.connect(slug_pre_save, sender=Taxon)
signals.pre_save.connect(update_delta, sender=Query)
signals.post_save.connect(update_results, sender=Query)
