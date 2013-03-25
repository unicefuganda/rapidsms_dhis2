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
from dhis2.templatetags.status_css_tag import *

ACTS_XFORM_ID = 55
COUNT_OF_TEST_TASK_SUBMISSION_LOGS = 5
COUNT_OF_TEST_TASK_LOGS = 15
TEST_USER_NAME = 'smoke'
TEST_USER_PASSWORD = 'password'
SLEEP_TIME_BEFORE_PAGE_LOAD_IN_SECONDS = 5
TASK_LOG_STATUS = [ Dhis2_Reports_Report_Task_Log.RUNNING, Dhis2_Reports_Report_Task_Log.FAILED, Dhis2_Reports_Report_Task_Log.SUCCESS]
DATE_TIME_FORMAT = "%b %d, %Y, %H:%M"

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
     status                = _generate_random_task_status(),
     description           = 'testing view for h033b reporter '
    )
    world.test_objects.append(task_log)
    
def _generate_random_task_status():
  status = random.randrange(0,3)
  if status == 0 :
    return Dhis2_Reports_Report_Task_Log.RUNNING
  if status == 1 : 
    return Dhis2_Reports_Report_Task_Log.FAILED
  return  Dhis2_Reports_Report_Task_Log.SUCCESS

@step('I see the navigation bar')
def see_logout_navigation_bar(step):
  assert world.browser.find_link_by_text('Home')
  assert world.browser.find_link_by_text('Dhis2Reporter')
  assert world.browser.find_link_by_partial_text('logout')

@step('I must see all submission tasks on the index page')
def show_submission_tasks(step):
  number_of_log_pages = max(ceil(len(Dhis2_Reports_Report_Task_Log.objects.all())/(TASK_LOG_RECORDS_PER_PAGE*1.0)),1)
  sleep(SLEEP_TIME_BEFORE_PAGE_LOAD_IN_SECONDS)
  assert world.browser.is_text_present("DHIS2 Reports Submissions")
  _find_task_log_table_headings()
  assert world.browser.is_text_present("<Page 1 of %d>"%number_of_log_pages)
  world.browser.is_element_present_by_css("a[class=next]", wait_time=3)
  world.browser.find_by_css("a[class=next]").first.click()
  _find_task_log_table_headings()
  assert world.browser.is_text_present("<Page 2 of %d>"%number_of_log_pages)

def _find_task_log_table_headings():
  assert world.browser.is_text_present("ID")
  assert world.browser.is_text_present("Time Started")
  assert world.browser.is_text_present("Result")
  assert world.browser.is_text_present("Summary")
  assert world.browser.is_text_present("Number of submissions")
  
@step(u'When I have a SUCCESS, RUNNING or FAILED tasks')
def create_success_running_failed_tasks_logs(step):
  world.browser.time_started = datetime.datetime(2013, 1, 1, 12, 12 , 12)
  Dhis2_Reports_Report_Task_Log.objects.all().delete()
  world.browser.submissions_count= len(RESULT_URLS) # minimum required if we were to tests all different types of log_submissions
  for status in TASK_LOG_STATUS :
     task_log = Dhis2_Reports_Report_Task_Log.objects.create(
     time_finished         = world.browser.time_started + datetime.timedelta(minutes=5),
     number_of_submissions = world.browser.submissions_count,
     status                = status,
     description           = status + ': testing view for h033b reporter ' )
     task_log.time_started = world.browser.time_started 
     task_log.save()
     world.test_objects.append(task_log)
    
     _create_task_submission_for_task_id(task_log.id, world.browser.submissions_count)

@step('Corresponding submission tasks details appears')
def show_task_details_contents(step):
  
  assert world.browser.is_text_present("DHIS2 Reports Submissions")
  NUMBER_OF_COLUMNS_IN_LOG_PAGE = 6
  
  for task in TASK_LOG_STATUS:
    task_css = get_task_css(task)
    log_entry = world.browser.find_by_css("tr."+ task_css).first.find_by_tag('td')
    log_entry_columns = [column.html.strip() for column in log_entry]
    
    assert len(log_entry_columns) == NUMBER_OF_COLUMNS_IN_LOG_PAGE

    assert world.browser.time_started.strftime(DATE_TIME_FORMAT) in log_entry_columns
    assert task in log_entry_columns
    assert str(world.browser.submissions_count) in log_entry_columns
    
    log_entry_columns = ",".join(log_entry_columns)
    for result in RESULT_URLS.keys():
      assert RESULT_URLS[result][0] in log_entry_columns
      assert RESULT_URLS[result][1] in log_entry_columns
  

@step(u'And I select a  task')
def select_a_task_log(step):
  world.browser.is_element_present_by_css("a[class=task_id]", wait_time=3)
  world.selected_task = world.browser.find_by_css("a[class=task_id]").first

@step(u'And I have some submissions for that task')
def create_some_submission_logs(step):
  world.task_id = int(world.selected_task.html)
  _create_task_submission_for_task_id(world.task_id,COUNT_OF_TEST_TASK_SUBMISSION_LOGS)

def _generate_random_task_submisison_status():
  return TASK_LOG_STATUS[random.randrange(len(status))] 

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
    
def _create_task_submission_for_task_id(task_id,submissions_count, result = RESULT_URLS.keys()[random.randrange(len(RESULT_URLS.keys()))]):
  # task = Dhis2_Reports_Report_Task_Log.objects.get(id=world.task_id)
  # submissions_tasks = Dhis2_Reports_Submissions_Log.objects.filter(task_id=task)
  
  task = Dhis2_Reports_Report_Task_Log.objects.get(id=task_id)
  xform_id = ACTS_XFORM_ID
  attributes_and_values = {
    u'epd': 53,
       u'eps': 62,
  }
  
  for x in range(submissions_count) :     
    submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility = None)
    
    result = RESULT_URLS.keys()[x%len(RESULT_URLS.keys())]
    xml , result,descrption = _create_random_submission_log_fields(result)
    
    log_record = Dhis2_Reports_Submissions_Log.objects.create(
      task_id               = task,
      submission_id         = submission.id,
      reported_xml          = xml,
      result                = result,
      description           = descrption
    )
    
    world.test_objects.append(submission)
    world.test_objects.append(log_record)
    
def _create_random_submission_log_fields(result):
  request_xml = '<dataValueSet xmlns="http://dhis2.org/schema/dxf/2.0" dataSet="V1kJRs8CtW4" completeDate="2013-01-21T23:59:59Z" \
  	period="2013W3" orgUnitIdScheme="uuid"  orgUnit="e8085011-b276-41ea-b5c0-a60bb4be61ef"  >\
      <dataValue dataElement="OMxmmYvvLai" categoryOptionCombo= "gGhClrV5odI" value="62" />\
  </dataValueSet>'
  
  return request_xml , result, RESULT_URLS[result][0]
   

