from dhis2.h033b_reporter import *
from celery.task.schedules import crontab  
from celery.decorators import periodic_task  
from celery import Celery, current_task

celery = Celery()
  
# this will at midnight on every Thursday of the week, see http://celeryproject.org/docs/reference/celery.task.schedules.html#celery.task.schedules.crontab 
@celery.task
def weekly_report_submissions_task(): 
  h033b_reporter = H033B_Reporter()
  h033b_reporter.initiate_weekly_submissions()


  
  