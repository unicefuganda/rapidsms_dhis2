from django.shortcuts import render, redirect
from django.http import HttpResponse ,HttpResponseRedirect
# import the template and template loader 
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from dhis2.models import Dhis2_Reports_Report_Task_Log,Dhis2_Reports_Submissions_Log

TASK_LOG_RECORDS_PER_PAGE = 10
TASK_SUBMISSIONS_LOG_RECORDS_PER_PAGE = 10

def index(request):
  task_logs = __get_tasks_view_data()
  paginator = Paginator(task_logs, TASK_LOG_RECORDS_PER_PAGE)
  page = request.GET.get('page')
  page = int(page) if page else 1
  
  try:
    task_logs_paginator = paginator.page(page)
  except PageNotAnInteger:
    task_logs_paginator = paginator.page(1)
  except EmptyPage:
    task_logs_paginator = paginator.page(paginator.num_pages)
  
  return render(request, 'h033b_reporter_index.html', {'tasks_logs_paginator':task_logs_paginator})

def __get_tasks_view_data():
  tasks = Dhis2_Reports_Report_Task_Log.objects.all()
  data = []
  for task in tasks : 
    task_view_data = task
    running_time_in_minutes = (task.time_finished - task.time_started).seconds/60 
    task_view_data.running_time = str(running_time_in_minutes)+' minutes'     
    data.append(task_view_data)
  
  return data  

def task_details(request,task_id):
  task = Dhis2_Reports_Report_Task_Log.objects.get(id=task_id)
  submissions_tasks = Dhis2_Reports_Submissions_Log.objects.filter(task_id=task)
  paginator = Paginator(submissions_tasks, TASK_SUBMISSIONS_LOG_RECORDS_PER_PAGE)
  page = request.GET.get('page')
  page = int(page) if page else 1
  
  try:
    task_submissions_paginator = paginator.page(page)
  except PageNotAnInteger:
    task_submissions_paginator = paginator.page(1)
  except EmptyPage:
    task_submissions_paginator = paginator.page(paginator.num_pages)
  
  return render(request, 'task_details.html', {'task_submissions_paginator':task_submissions_paginator})
  

     
     