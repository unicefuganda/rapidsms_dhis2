from dhis2.h033b_reporter import *
from celery.task import task
import urllib2
from datetime import datetime

@task
def weekly_report_submissions_task(date=datetime.now()): 
  h033b_reporter = H033B_Reporter()
  h033b_reporter.initiate_weekly_submissions(date=date)

@task
def submit_reports_now_task(submissions): 
  h033b_reporter = H033B_Reporter()
  h033b_reporter.submit_and_log_task_now(submissions)

