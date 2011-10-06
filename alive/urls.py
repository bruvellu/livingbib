from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from views import *

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

urlpatterns = patterns('',
        url(r'^$', home_page),
        url(r'^search/$', search_page),
        url(r'^taxa/$', taxa_page),
        url(r'^taxon/(?P<slug>[^\d]+)/$', taxon_page, name='taxon_url'),
        url(r'^user/(?P<slug>[^\d]+)/$', user_page, name='user_url'),

        # Auth
        (r'^login/$', 'django.contrib.auth.views.login'),
        (r'^logout/$', 'django.contrib.auth.views.logout'),

        (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
)
