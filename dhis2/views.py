from django.shortcuts import render, redirect
from django.http import HttpResponse ,HttpResponseRedirect
from django.contrib import messages
# import the template and template loader 
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from healthmodels.models.HealthFacility import *
from rapidsms_xforms.models import XForm

from dhis2.h033b_reporter import *
from dhis2.models import Dhis2_Reports_Report_Task_Log,Dhis2_Reports_Submissions_Log
from dhis2.reports_submission_tasks import *

from datetime import datetime, timedelta

TASK_LOG_RECORDS_PER_PAGE = 10
TASK_SUBMISSIONS_LOG_RECORDS_PER_PAGE = 10

RESULT_URLS = {
    Dhis2_Reports_Submissions_Log.SUCCESS                 : [' Successful submissions', ''], # we provide no urls for success -- too many and no need for them
    Dhis2_Reports_Submissions_Log.FAILED                  : [' Network failure or other failed submissions','failed'],
    Dhis2_Reports_Submissions_Log.ERROR                   : [' With invalid orgUnit or diseases ID changed','errors'],
    Dhis2_Reports_Submissions_Log.INVALID_SUBMISSION_DATA : [' No HMIS033b indicators','non-hmis-indicators'], 
    Dhis2_Reports_Submissions_Log.NON_REPORTING_FACILITIES : [' Non HMIS033b reporting facilities','non-hmis-facilities'], 
    Dhis2_Reports_Submissions_Log.SOME_ATTRIBUTES_IGNORED : [' Ignored', 'ignored'],
}

def index(request):
  task_logs = _get_tasks_view_data()
  sorter_by_start_time = lambda data : data.time_started
  task_logs = sorted(task_logs,key=sorter_by_start_time, reverse=True)
  task_logs_paginator = _paginate(request, task_logs)
  
  return render(request, 'h033b_reporter_index.html', {'tasks_logs_paginator':task_logs_paginator})

def task_failed(request,task_id):
  return _generate_log_page(request=request, task_id=task_id, result = Dhis2_Reports_Submissions_Log.FAILED, view_html='failed.html')

def task_errors(request,task_id):
  return _generate_log_page(request=request, task_id=task_id, result = Dhis2_Reports_Submissions_Log.ERROR, view_html='log_details.html')

def task_ignored(request,task_id):
  return _generate_log_page(request=request, task_id=task_id, result = Dhis2_Reports_Submissions_Log.SOME_ATTRIBUTES_IGNORED, view_html='log_details.html')
  
def task_summary(request,task_id):
  task = Dhis2_Reports_Report_Task_Log.objects.get(id=task_id)

  all_sub=[]

  for result in RESULT_URLS.keys():
    log_result = Dhis2_Reports_Submissions_Log.objects.filter(task_id=task, result=result)
    
    if log_result:
     a_result = log_result[0]
     a_result.size = len(log_result) 
     a_result.url = RESULT_URLS[result][1] if RESULT_URLS[result][1] else None
     all_sub.append(a_result)
    
  teplate_data = {
    'task_log'  : task,
    'results'    : all_sub,
  }

  return render(request, 'submission_summary.html', teplate_data)
  
def resubmit_failed(request, task_id):
  running_tasks = Dhis2_Reports_Report_Task_Log.objects.filter(status = Dhis2_Reports_Report_Task_Log.RUNNING)
  if running_tasks and datetime.now()-running_tasks.latest('time_started').time_started < timedelta(hours=2):
    messages.error(request, "Submission aborted: other submissions launched less than two hours ago! Relaunch submission later.")
    return redirect(reverse('dhis2_reporter_index_page'))     
  
  h033b_reporter = H033B_Reporter()
  task = Dhis2_Reports_Report_Task_Log.objects.get(id=task_id)
  submission_log = Dhis2_Reports_Submissions_Log.objects.filter(task_id=task, result=Dhis2_Reports_Submissions_Log.FAILED)
  ids_of_failed_submissions = list(set(submission_log.values_list('submission_id', flat = True)))
  submissions = XFormSubmission.objects.filter(id__in= ids_of_failed_submissions)
  submissions = h033b_reporter.set_submissions_facility(submissions)
 
  submit_reports_now_task.delay(submissions)
  messages.success(request, "Submission has started! Please refresh in few minutes.")
  return redirect(reverse('dhis2_reporter_index_page'))     
  

def _get_tasks_view_data():
  tasks = Dhis2_Reports_Report_Task_Log.objects.all()
  data = []
  for task in tasks : 
    task_view_data = task
    task.time_finished = task.time_finished if task.time_finished else datetime.now() 
    running_time_in_minutes = (task.time_finished - task.time_started).seconds/60 
    task_view_data.running_time = str(running_time_in_minutes)+' minutes'  
    task_view_data.details = _get_task_details(task)   
    data.append(task_view_data)

  return data
  
def _get_task_details(task):
  task_details=[]

  for result in RESULT_URLS.keys():
    log_result = Dhis2_Reports_Submissions_Log.objects.filter(task_id=task, result=result)

    if log_result:
      a_result = {}
      a_result['description'] = RESULT_URLS[result][0]
      a_result['size'] = len(log_result) 
      a_result['url'] = RESULT_URLS[result][1] if RESULT_URLS[result][1] else None
      task_details.append(a_result)

  return task_details
  
def _generate_log_page(request, task_id, result, view_html):
  task = Dhis2_Reports_Report_Task_Log.objects.get(id=task_id)
  submissions_tasks = Dhis2_Reports_Submissions_Log.objects.filter(task_id=task, result=result)
  task_submissions_paginator = _paginate(request, submissions_tasks)

  task.show_resubmit_button= Dhis2_Reports_Submissions_Log.objects.filter(task_id=task, result=Dhis2_Reports_Submissions_Log.FAILED)
 
  teplate_data = {
    'task_log'  : task,
    'task_submissions_paginator':task_submissions_paginator,
    }

  return render(request, view_html, teplate_data)

def task_non_hmis_facilities(request,task_id):
  task = Dhis2_Reports_Report_Task_Log.objects.get(id=task_id)
  result = Dhis2_Reports_Submissions_Log.NON_REPORTING_FACILITIES
  submissions_tasks = Dhis2_Reports_Submissions_Log.objects.filter(task_id=task, result=result)
  
  facility_list = list(set(submissions_tasks.values_list('reported_xml', flat=True)))
  non_hmis_data =[]
  
  for facility_id in facility_list:
    associated_facility = submissions_tasks.filter(reported_xml = facility_id)
    submission_ids = list(set(associated_facility.values_list('id', flat=True)))
    facility ={'facility': HealthFacilityBase.objects.get(id=facility_id),
                'submission': str(submission_ids).strip('[]')
                }
    non_hmis_data.append(facility)
 
  task_submissions_paginator = _paginate(request, non_hmis_data)
 
  teplate_data = {
    'task_log'  : task,
    'task_submissions_paginator':task_submissions_paginator,
   }
  return render(request, 'non_hmis_facility.html', teplate_data)

def task_non_hmis_indicators(request,task_id):
  task = Dhis2_Reports_Report_Task_Log.objects.get(id=task_id)
  result = Dhis2_Reports_Submissions_Log.INVALID_SUBMISSION_DATA
  submissions_tasks = Dhis2_Reports_Submissions_Log.objects.filter(task_id=task, result=result)
  
  xform_list = list(set(submissions_tasks.values_list('reported_xml', flat=True)))
  print xform_list
  xform_detail =[]
  for xform_id in xform_list:
    detail={'xform': XForm.objects.get(id=int(xform_id)),
            'number': len(submissions_tasks.filter(reported_xml=xform_id))
            }
    xform_detail.append(detail)        

  teplate_data = {
    'task_log'  : task,
    'xform_details':xform_detail,
   }
  return render(request, 'non_hmis_indicators.html', teplate_data)

def _paginate(request, submissions_tasks):
  paginator = Paginator(submissions_tasks, TASK_SUBMISSIONS_LOG_RECORDS_PER_PAGE)
  page = request.GET.get('page')
  page = int(page) if page else 1
  
  try:
    task_submissions_paginator = paginator.page(page)
  except PageNotAnInteger:
    task_submissions_paginator = paginator.page(1)
  except EmptyPage:
    task_submissions_paginator = paginator.page(paginator.num_pages)
  
  return task_submissions_paginator
    
