from django.test import TestCase
from dhis2.models import Dhis2_Reports_Submissions_Log ,Dhis2_Reports_Report_Task_Log
import datetime

class Test_Dhis2_Models(TestCase) :
    
  def test_dhis2_reports_submissions_log(self) : 
    task_id = Dhis2_Reports_Report_Task_Log.objects.create()
    report_submissions_log = Dhis2_Reports_Submissions_Log.objects.create(
      task_id = task_id,
      submission_id = 1
      )
    self.failUnless(report_submissions_log.id)
  
    report_submissions_log = Dhis2_Reports_Submissions_Log.objects.create(
      task_id = task_id,
      submission_id = 1,
      reported_xml = 1, 
      result = Dhis2_Reports_Report_Task_Log.SUCCESS,
      description ='No Description', 
      )
    self.failUnless(report_submissions_log.id)

  def test_dhis2_reports_report_task_log_default(self):
    time_before_log = datetime.datetime.now()
    task = Dhis2_Reports_Report_Task_Log.objects.create()
    time_after_log = datetime.datetime.now()

    assert time_after_log - time_before_log > time_after_log - task.time_started


  def test_dhis2_reports_report_task_log_values(self):
    time_before_log = datetime.datetime.now()
    
    task = Dhis2_Reports_Report_Task_Log.objects.create(
      time_finished         = datetime.datetime.now() ,
      number_of_submissions = 23 ,
      status                = Dhis2_Reports_Report_Task_Log.RUNNING ,
      description           = 'No description'
    )
    time_after_log = datetime.datetime.now()

    assert time_after_log - time_before_log > time_after_log - task.time_started
    
    self.failUnless(task.id)
    self.failUnless(Dhis2_Reports_Report_Task_Log.FAILED)
    self.failUnless(Dhis2_Reports_Report_Task_Log.SUCCESS)

