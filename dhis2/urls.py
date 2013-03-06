from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('dhis2.views',
    url(r'^$', 'index'),
)

