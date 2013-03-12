# -*- coding: utf-8 -*-
from lettuce import *
from splinter import Browser
from lettuce.django import django_url
from dhis2.models import Dhis2_Reports_Report_Task_Log
import datetime
import random 
from dhis2.views import *
from math import *
from dhis2.tests.test_helper import *
from time import sleep

ACTS_XFORM_ID = 55
COUNT_OF_TEST_TASK_SUBMISSION_LOGS = 5
COUNT_OF_TEST_TASK_LOGS = 15
TEST_USER_NAME = 'smoke'
TEST_USER_PASSWORD = 'password'
SLEEP_TIME_BEFORE_PAGE_LOAD_IN_SECONDS = 5

@before.each_scenario
def set_browser(scenario):
  world.test_objects = []
  world.browser = Browser()

@after.each_scenario
def close_browser(scenario):
  world.browser.quit()
  delete_test_objets() 
 
def delete_test_objets():
 for test_object in world.test_objects :
     test_object.delete()

@step(u'And I am logged in')
def log_in(step):
 visit("/dhis2reporter/")
 world.browser.fill("username", TEST_USER_NAME)
 world.browser.fill("password", TEST_USER_PASSWORD)
 world.browser.find_by_css('input[type=submit]').first.click()

def visit(url):
 world.browser.visit(django_url(url))

@step(u'Given I have some submission tasks run')
def create_some_logs(step):
  for count in range(COUNT_OF_TEST_TASK_LOGS) :
    task_log = Dhis2_Reports_Report_Task_Log.objects.create(
     time_finished         = datetime.datetime.now(),
     number_of_submissions = random.randrange(0,999999),
     status                = __generate_random_task_status(),
     description           = 'testing view for h033b reporter '
    )
    world.test_objects.append(task_log)
    
def __generate_random_task_status():
  status = random.randrange(0,3)
  if status == 0 :
    return Dhis2_Reports_Report_Task_Log.RUNNING
  if status == 1 : 
    return Dhis2_Reports_Report_Task_Log.FAILED
  return  Dhis2_Reports_Report_Task_Log.SUCCESS

@step('I must see all submission tasks on the index page')
def show_submission_tasks(step):
  number_of_log_pages = max(ceil(len(Dhis2_Reports_Report_Task_Log.objects.all())/(TASK_LOG_RECORDS_PER_PAGE*1.0)),1)
  sleep(SLEEP_TIME_BEFORE_PAGE_LOAD_IN_SECONDS)
  assert world.browser.is_text_present("ID")
  assert world.browser.is_text_present("Time Started")
  assert world.browser.is_text_present("Result")
  assert world.browser.is_text_present("Description")
  assert world.browser.is_text_present("Number of submissions")
  assert world.browser.is_text_present("<Page 1 of %d>"%number_of_log_pages)
  world.browser.is_element_present_by_css("a[class=next]", wait_time=3)
  world.browser.find_by_css("a[class=next]").first.click()
  assert world.browser.is_text_present("ID")
  assert world.browser.is_text_present("Time Started")
  assert world.browser.is_text_present("Result")
  assert world.browser.is_text_present("Description")
  assert world.browser.is_text_present("Number of submissions")
  assert world.browser.is_text_present("<Page 2 of %d>"%number_of_log_pages)


@step(u'And I select a  task')
def select_a_task_log(step):
  world.browser.is_element_present_by_css("a[class=task_id]", wait_time=3)
  world.selected_task = world.browser.find_by_css("a[class=task_id]").first

@step(u'And I have some submissions for that task')
def create_some_submission_logs(step):
  world.task_id = int(world.selected_task.html)
  __create_task_submission_for_task_id(world.task_id,COUNT_OF_TEST_TASK_SUBMISSION_LOGS)

def __generate_random_task_submisison_status():
  status=[
    Dhis2_Reports_Report_Task_Log.SUCCESS ,
    Dhis2_Reports_Report_Task_Log.FAILED ,
    Dhis2_Reports_Report_Task_Log.RUNNING
  ]
  return status[random.randrange(len(status))] 

@step('And I open details page for the task')
def open_details_page_for_selected_task(step):
  world.selected_task.click()
  

@step(u'Then the corresponding task details page appears')
def test_task_details_page(step):
  task = Dhis2_Reports_Report_Task_Log.objects.get(id=world.task_id)
  submissions_tasks= Dhis2_Reports_Submissions_Log.objects.filter(task_id=task)
  number_of_submission_pages = max(ceil (len(submissions_tasks)/(TASK_SUBMISSIONS_LOG_RECORDS_PER_PAGE*1.0)),1)
  sleep(SLEEP_TIME_BEFORE_PAGE_LOAD_IN_SECONDS)
  assert world.browser.is_text_present("Submissions ID")
  assert world.browser.is_text_present("Report XML")
  assert world.browser.is_text_present("Result")
  assert world.browser.is_text_present("Description")
  assert world.browser.is_text_present("<Page 1 of %d>"%number_of_submission_pages)  
    
def __create_task_submission_for_task_id(task_id,submissions_count):
  task = Dhis2_Reports_Report_Task_Log.objects.get(id=world.task_id)
  submissions_tasks = Dhis2_Reports_Submissions_Log.objects.filter(task_id=task)
  
  task = Dhis2_Reports_Report_Task_Log.objects.get(id=task_id)
  xform_id = ACTS_XFORM_ID
  attributes_and_values = {
    u'epd': 53,
       u'eps': 62,
  }
  
  for x in range(submissions_count) :     
    submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility = None)

    xml , result,descrption = __create_random_submission_log_fields()
    
    log_record = Dhis2_Reports_Submissions_Log.objects.create(
      task_id               = task,
      submission_id         = submission.id,
      reported_xml          = xml,
      result                = result,
      description           = descrption
    )
    
    world.test_objects.append(submission)
    world.test_objects.append(log_record)
    
def __create_random_submission_log_fields():
  request_xml = '<dataValueSet xmlns="http://dhis2.org/schema/dxf/2.0" dataSet="V1kJRs8CtW4" completeDate="2013-01-21T23:59:59Z" \
  	period="2013W3" orgUnitIdScheme="uuid"  orgUnit="e8085011-b276-41ea-b5c0-a60bb4be61ef"  >\
      <dataValue dataElement="OMxmmYvvLai" categoryOptionCombo= "gGhClrV5odI" value="62" />\
  </dataValueSet>'
  
  results=[
    Dhis2_Reports_Submissions_Log.SUCCESS ,
    Dhis2_Reports_Submissions_Log.INVALID_SUBMISSION_DATA ,
    Dhis2_Reports_Submissions_Log.SOME_ATTRIBUTES_IGNORED ,
    Dhis2_Reports_Submissions_Log.ERROR
  ]
  
  descrption = {
    Dhis2_Reports_Submissions_Log.SUCCESS :'succesfully submitted all data',
    Dhis2_Reports_Submissions_Log.INVALID_SUBMISSION_DATA  :'Some data invalid',
    Dhis2_Reports_Submissions_Log.SOME_ATTRIBUTES_IGNORED  :'not all attributes ',
    Dhis2_Reports_Submissions_Log.ERROR  :'Error.....some submission are crappy dude !!!'
  }
  result = results[random.randrange(len(results))]
  return request_xml , result, descrption[result]
   

