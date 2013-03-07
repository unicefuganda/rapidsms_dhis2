from django.conf.urls.defaults import patterns, include, url
from dhis2.views import *
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('dhis2.views',
    url(r'^$', login_required(index),name='dhis2_reporter_index_page'),
)

