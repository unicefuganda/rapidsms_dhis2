from lettuce import *
from dhis2.h033b_reporter import *
import datetime
from healthmodels.models.HealthFacility import HealthFacilityBase
import urllib2, vcr, os, dhis2, sys
from dhis2.tests.test_helper import Submissions_Test_Helper

h033b_reporter = H033B_Reporter()

NO_SUBMISSION_EXTRA_SUBMISSION_ID = 365988
NO_VALID_HMS_ATTRIBUTE_SUBMISSION_ID = 365400
SOME_ATTRIBUTES_IGNORED_SUBMISSION_ID = 416117

DUMMY_HEALTHFACILITY_UUID_MAPPINGS = {
  515 : '6VeE8JrylXn',
}

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
def xformsubmissionextras_does_not_exist(step):
  Submissions_Test_Helper.xformsubmissionextras_does_not_exist(NO_SUBMISSION_EXTRA_SUBMISSION_ID)

@step(u'Must make correct log table entries where no valid indicators exist')
def no_valid_hms_indicator_exists(step):
  Submissions_Test_Helper.no_valid_hms_indicator_exists(NO_VALID_HMS_ATTRIBUTE_SUBMISSION_ID)

@step(u'Must make correct log table entries where some indicators ignored by dhis2')
def dhis2_returns_error(self):
  Submissions_Test_Helper.dhis2_returns_error(SOME_ATTRIBUTES_IGNORED_SUBMISSION_ID)

@after.all
def teardown(*args):
  for health_facility_base_id in DUMMY_HEALTHFACILITY_UUID_MAPPINGS : 
    facility = HealthFacilityBase.objects.get(id=health_facility_base_id)
    facility.uuid = None
    facility.save(cascade_update=False)

