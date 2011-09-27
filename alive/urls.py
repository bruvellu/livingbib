from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from views import *

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

urlpatterns = patterns('',
        url(r'^$', home_page),
        url(r'^search/$', search_page),
        url(r'^taxon/(?P<slug>[^\d]+)/$', taxon_page, name='taxon_url'),
        (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
)
