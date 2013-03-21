from dhis2.h033b_reporter import *
from celery import Celery
import urllib2

celery = Celery()

@celery.task
def weekly_report_submissions_task(date): 
  h033b_reporter = H033B_Reporter()
  h033b_reporter.initiate_weekly_submissions(date=date)

@celery.task
def post(self, request):
  return urllib2.urlopen(request)  
