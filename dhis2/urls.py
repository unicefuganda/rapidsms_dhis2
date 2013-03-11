from django.conf.urls.defaults import patterns, include, url
from dhis2.views import *
from django.contrib.auth.decorators import login_required
from rapidsms.views import logout as rapidsms_logout

urlpatterns = patterns('dhis2.views',
    url(r'^$', login_required(index),name='dhis2_reporter_index_page'),
    url(r'^(\d+)/$', login_required(task_details),name='task_details'),
    url(r'^logout$', rapidsms_logout, name="logout_dhis2")  
)

