from django.conf.urls.defaults import patterns, include, url
from views import *

urlpatterns = patterns('',
        url(r'^$', home_page),
        url(r'^search/$', search_page),
        url(r'^taxon/(?P<slug>[^\d]+)/$', taxon_page, name='taxon_url'),
)
