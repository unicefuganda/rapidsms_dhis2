from django.conf.urls.defaults import patterns, include, url
from dhis2.views import *
from django.contrib.auth.decorators import login_required
from rapidsms.views import logout as rapidsms_logout

urlpatterns = patterns('dhis2.views',
    url(r'^$', login_required(index),name='dhis2_reporter_index_page'),
    url(r'^(\d+)/errors$', login_required(task_errors),name='task_errors'),
    url(r'^(\d+)/$', login_required(task_summary),name='task_summary'),
    url(r'^(\d+)/failed$', login_required(task_failed),name='task_failed'),        
    url(r'^(\d+)/ignored$', login_required(task_ignored),name='task_ignored'),
    url(r'^(\d+)/failed/submit$', login_required(resubmit_failed),name="re_submit_failed"),                
    url(r'^logout$', rapidsms_logout, name="logout_dhis2")  
)

