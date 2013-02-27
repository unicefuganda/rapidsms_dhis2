from lettuce import *
from dhis2.h033b_reporter import *
import datetime
from healthmodels.models.HealthFacility import HealthFacilityBase
import urllib2, vcr, os, dhis2, sys

h033b_reporter = H033B_Reporter()

NO_SUBMISSION_EXTRA_SUBMISSION_ID = 365988
NO_VALID_HMS_ATTRIBUTE_SUBMISSION_ID = 365400
SOME_ATTRIBUTES_IGNORED_SUBMISSION_ID = 416117

DUMMY_HEALTHFACILITY_UUID_MAPPINGS = {
  515 : '6VeE8JrylXn',
}

FIXTURES = os.path.abspath(dhis2.__path__[0]) + "/tests/fixtures/cassettes/"

@before.all
def setup():
  for health_facility_base_id in DUMMY_HEALTHFACILITY_UUID_MAPPINGS : 
    facility = HealthFacilityBase.objects.get(id=health_facility_base_id)
    facility.uuid = DUMMY_HEALTHFACILITY_UUID_MAPPINGS[health_facility_base_id]
    facility.save(cascade_update=False)

@step(u'Report data must have all valid fields')
def get_reports_data_for_submission(self):
  submission = XFormSubmission.objects.get(id=SOME_ATTRIBUTES_IGNORED_SUBMISSION_ID)
  submission_time  = datetime.datetime(2013, 2, 5, 14, 53, 57, 616928)    
  data  =  h033b_reporter.get_reports_data_for_submission(XFormSubmissionExtras.objects.filter(submission=submission))
  submission_values = XFormSubmissionValue.objects.filter(submission=submission)
  h033b_reporter.set_data_values_from_submission_value(data,submission_values)
  
  assert data['orgUnit'] == DUMMY_HEALTHFACILITY_UUID_MAPPINGS[515]
  # assert data['completeDate'] == submission_time
  assert data['period'] == '2013W5'
  assert len(data['dataValues']) ==2
  
  assert data['dataValues'][0]['dataElement'] == u'ck3jFjr8fOT' 
  assert data['dataValues'][0]['categoryOptionCombo'] ==  u'gGhClrV5odI'
  assert data['dataValues'][0]['value'] ==  0
  
  assert data['dataValues'][1]['dataElement'] == u'nG5hrCX3vyP' 
  assert data['dataValues'][1]['categoryOptionCombo'] ==  u'gGhClrV5odI'
  assert data['dataValues'][1]['value'] ==  0

@step(u'Must fetch all submissions made within the specified period')
def get_submissions_in_date_range(self):
  from_date = datetime.datetime(2011, 12, 18, 00, 00, 00)
  to_date = datetime.datetime(2011, 12, 19, 23, 59, 59)
  submissions_in_period  = h033b_reporter.get_submissions_in_date_range(from_date,to_date)
  assert len(submissions_in_period) == 314

@step(u'Must make correct log table entries where XFormSubmissionExtras doesnt exist')
def scenario_data_generation(step):
  h033b_reporter.log_submission_started()
  submission = XFormSubmission.objects.get(id=NO_SUBMISSION_EXTRA_SUBMISSION_ID)
  h033b_reporter.get_data_submission(submission)
  log = Dhis2_Reports_Submissions_Log.objects.filter(task_id=h033b_reporter.current_task)[0]
 
  assert not log.reported_xml
  assert log.task_id        == h033b_reporter.current_task
  assert log.submission_id  == submission.id
  assert log.result         == Dhis2_Reports_Submissions_Log.INVALID_SUBMISSION_DATA
  assert log.description    == ERROR_MESSAGE_NO_SUBMISSION_EXTRA

@step(u'Must make correct log table entries where no valid indicators exist')
def scenario_data_generation(step):
  h033b_reporter.log_submission_started()
  submission = XFormSubmission.objects.get(id=NO_VALID_HMS_ATTRIBUTE_SUBMISSION_ID)
  h033b_reporter.get_data_submission(submission)
  log = Dhis2_Reports_Submissions_Log.objects.filter(task_id=h033b_reporter.current_task)
  log = log[len(log)-1]
  
  assert not log.reported_xml
  assert log.task_id        == h033b_reporter.current_task
  assert log.submission_id  == submission.id
  assert log.result         == Dhis2_Reports_Submissions_Log.INVALID_SUBMISSION_DATA
  assert log.description    == ERROR_MESSAGE_NO_HMS_INDICATOR

@step(u'Must make correct log table entries where some indicators ignored by dhis2')
def test_submit_faliure_ignored_some(self):
  h033b_reporter.log_submission_started()
  submission = XFormSubmission.objects.get(id=SOME_ATTRIBUTES_IGNORED_SUBMISSION_ID)
  
  crapped_attribute_id,crapped_uuid_backup = corrupt_submission_attribute_mapping(submission)
  try :
    with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
      result = h033b_reporter.submit_submission(submission)
  finally:
    restore_submission_attribute_mapping(crapped_attribute_id,crapped_uuid_backup)

  log = Dhis2_Reports_Submissions_Log.objects.filter(task_id=h033b_reporter.current_task)[0]
  assert log.reported_xml
  assert log.task_id        == h033b_reporter.current_task
  assert log.submission_id  == submission.id
  assert log.result         == Dhis2_Reports_Submissions_Log.ERROR
  assert log.description    

def corrupt_submission_attribute_mapping(submission):
  for submission_value in XFormSubmissionValue.objects.filter(submission=submission) :
    crapped_attribute_id = submission_value.attribute_id
    mapping = Dhis2_Mtrac_Indicators_Mapping.objects.filter(mtrac_id=crapped_attribute_id)
    if mapping : 
      mapping=mapping[0]
      break

  crapped_uuid_backup = mapping.dhis2_uuid
  mapping.dhis2_uuid = u'CRAPPED'
  mapping.save()
  return crapped_attribute_id,crapped_uuid_backup
  
def restore_submission_attribute_mapping(crapped_attribute_id,crapped_uuid_backup):
  mapping = Dhis2_Mtrac_Indicators_Mapping.objects.filter(mtrac_id=crapped_attribute_id)[0]
  mapping.dhis2_uuid = crapped_uuid_backup
  mapping.save()
 
@after.all
def teardown(*args):
  for health_facility_base_id in DUMMY_HEALTHFACILITY_UUID_MAPPINGS : 
    facility = HealthFacilityBase.objects.get(id=health_facility_base_id)
    facility.uuid = None
    facility.save(cascade_update=False)

