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
from dhis2.views import *
from math import *
from dhis2.tests.test_helper import Submissions_Test_Helper

COUNT_OF_TEST_TASK_LOGS = 15 
TEST_USER_NAME = 'smoke'
TEST_USER_PASSWORD = 'password'

@before.each_scenario
def set_browser(scenario):
  world.browser = Browser()

@after.each_scenario
def close_browser(scenario):
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
  number_of_log_pages = max(ceil(len(Dhis2_Reports_Report_Task_Log.objects.all())/TASK_LOG_RECORDS_PER_PAGE),1)
  
  print '*'*100
  print number_of_log_pages
  print len(Dhis2_Reports_Report_Task_Log.objects.all())/TASK_LOG_RECORDS_PER_PAGE
  print len(Dhis2_Reports_Report_Task_Log.objects.all())
  print '*'*100
  assert world.browser.is_text_present("ID")
  assert world.browser.is_text_present("Time Started")
  assert world.browser.is_text_present("Result")
  assert world.browser.is_text_present("Descrition")
  assert world.browser.is_text_present("Number of submissions")
  assert world.browser.is_text_present("<Page 1 of %d>"%number_of_log_pages)
  world.browser.is_element_present_by_css("a[class=next]", wait_time=3)
  world.browser.find_by_css("a[class=next]").first.click()
  assert world.browser.is_text_present("ID")
  assert world.browser.is_text_present("Time Started")
  assert world.browser.is_text_present("Result")
  assert world.browser.is_text_present("Descrition")
  assert world.browser.is_text_present("Number of submissions")
  assert world.browser.is_text_present("<Page 2 of %d>"%number_of_log_pages)


@step(u'And I select a  task')
def select_a_task_log(step):
  world.browser.is_element_present_by_css("a[class=task_id]", wait_time=3)
  world.selected_task_id = world.browser.find_by_css("a[class=task_id]").first.html
  world.browser.find_by_css("a[class=task_id]").first.click()

@step(u'And I have some submissions for that task')
def create_some_submission_logs(step):
  world.test_tasks_created = []
  for count in range(COUNT_OF_TEST_TASK_LOGS) :
    task_log = Dhis2_Reports_Report_Task_Log.objects.create(
     time_finished         = datetime.datetime.now(),
     number_of_submissions = random.randrange(0,999999),
     status                = __generate_random_status(),
     description           = 'testing view for h033b reporter '
    )
    world.test_tasks_created.append(task_log)


@step(u'Then the corresponding task details page appears')
def select_a_task_log(step):
  task = Dhis2_Reports_Report_Task_Log.objects.get(id= int(world.selected_task_id))
  submissions_tasks = Dhis2_Reports_Submissions_Log.objects.filter(task_id=task)
  
  number_of_submission_pages = max(ceil (len(submissions_tasks)/TASK_SUBMISSIONS_LOG_RECORDS_PER_PAGE),1)
  
  assert world.browser.is_text_present("Submissions ID")
  assert world.browser.is_text_present("Report XML")
  assert world.browser.is_text_present("Result")
  assert world.browser.is_text_present("Description")
  assert world.browser.is_text_present("<Page 1 of %d>"%number_of_submission_pages)  
  
  

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
  

