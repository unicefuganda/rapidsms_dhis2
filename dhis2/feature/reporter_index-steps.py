# -*- coding: utf-8 -*-
from lettuce import *
from lxml import html
from django.test.client import Client
from nose.tools import assert_equals
from splinter import Browser
from lettuce.django import django_url
from time import sleep
from random import randint
from datetime import datetime
import reversion, json
from dhis2.models import Dhis2_Reports_Report_Task_Log
import datetime
import random 

COUNT_OF_TEST_TASK_LOGS = 15 
TEST_USER_NAME = 'smoke'
TEST_USER_PASSWORD = 'password'

@before.all
def set_browser():
  world.browser = Browser()

@after.all
def close_browser(*args):
  world.browser.quit()
  
@step(u'Given I have some submission tasks run')
def create_some_logs(step):
  world.test_tasks_created = []
  for count in range(COUNT_OF_TEST_TASK_LOGS) :
    task_log = Dhis2_Reports_Report_Task_Log.objects.create(
     time_finished         = datetime.datetime.now(),
     number_of_submissions = random.randrange(0,999999),
     status                = __generate_random_status(),
     description           = 'testing view for h033b reporter '
    )
    world.test_tasks_created.append(task_log)
    
def __generate_random_status():
  status = random.randrange(0,3)
  if status == 0 :
    return Dhis2_Reports_Report_Task_Log.RUNNING
  if status == 1 : 
    return Dhis2_Reports_Report_Task_Log.FAILED
  return  Dhis2_Reports_Report_Task_Log.SUCCESS

@step('I must see all submission tasks on the index page')
def show_submission_tasks(step):
  sleep(4)
  pass
  
@step(u'Delete the test task logs created')
def delete_test_logs(step):
  for test_task in world.test_tasks_created :
      test_task.delete()
     

@step(u'And I am logged in')
def log_in(step):
  visit("/dhis2reporter/")
  world.browser.fill("username", TEST_USER_NAME)
  world.browser.fill("password", TEST_USER_PASSWORD)
  world.browser.find_by_css('input[type=submit]').first.click()
  
def visit(url):
  world.browser.visit(django_url(url))
  

