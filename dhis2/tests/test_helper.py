from lettuce import *
from dhis2.h033b_reporter import *
import datetime
from healthmodels.models.HealthFacility import HealthFacilityBase
import urllib2, vcr, os, dhis2, sys
from eav.models import Attribute ,Value
from mtrack.models import XFormSubmissionExtras
from rapidsms_xforms.models import XFormSubmissionValue, XForm, XFormSubmission
from dhis2.models import Dhis2_Temp_Mtrac_Indicators_Mapping

FIXTURES = os.path.abspath(dhis2.__path__[0]) + "/tests/fixtures/cassettes/"

class Submissions_Test_Helper(object):
  
  @classmethod
  def xformsubmissionextras_does_not_exist(self,submission_id):
    h033b_reporter = H033B_Reporter()
    h033b_reporter.log_submission_started()
    submission = XFormSubmission.objects.get(id=submission_id)
    h033b_reporter.get_data_submission(submission)
    log = Dhis2_Reports_Submissions_Log.objects.filter(task_id=h033b_reporter.current_task)[0]

    assert not log.reported_xml
    assert log.task_id        == h033b_reporter.current_task
    assert log.submission_id  == submission.id
    assert log.result         == Dhis2_Reports_Submissions_Log.INVALID_SUBMISSION_DATA
    assert log.description    == ERROR_MESSAGE_NO_SUBMISSION_EXTRA

  @classmethod
  def no_valid_hms_indicator_exists(self,submission_id):
    h033b_reporter = H033B_Reporter()
    h033b_reporter.log_submission_started()
    submission = XFormSubmission.objects.get(id=submission_id)
    h033b_reporter.get_data_submission(submission)
    log = Dhis2_Reports_Submissions_Log.objects.filter(task_id=h033b_reporter.current_task)
    log = log[len(log)-1]
  
    assert not log.reported_xml
    assert log.task_id        == h033b_reporter.current_task
    assert log.submission_id  == submission.id
    assert log.result         == Dhis2_Reports_Submissions_Log.INVALID_SUBMISSION_DATA
    assert log.description    == ERROR_MESSAGE_NO_HMS_INDICATOR

  @classmethod
  def dhis2_returns_error(self,submission_id):
    h033b_reporter = H033B_Reporter()
    h033b_reporter.log_submission_started()
    submission = XFormSubmission.objects.get(id=submission_id)
  
    crapped_attribute_id,crapped_uuid_backup = self.corrupt_submission_attribute_mapping(submission)
    try :
      with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
        result = h033b_reporter.submit_submission(submission)
    finally:
      self.restore_submission_attribute_mapping(crapped_attribute_id,crapped_uuid_backup)

    log = Dhis2_Reports_Submissions_Log.objects.filter(task_id=h033b_reporter.current_task)[0]
    

    assert log.reported_xml
    assert log.task_id        == h033b_reporter.current_task
    assert log.submission_id  == submission.id
    assert log.result         == Dhis2_Reports_Submissions_Log.ERROR
    assert log.description    

  @classmethod
  def corrupt_submission_attribute_mapping(self,submission):
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

  @classmethod
  def restore_submission_attribute_mapping(self,crapped_attribute_id,crapped_uuid_backup):
    mapping = Dhis2_Mtrac_Indicators_Mapping.objects.filter(mtrac_id=crapped_attribute_id)[0]
    mapping.dhis2_uuid = crapped_uuid_backup
    mapping.save()
    
  @classmethod  
  def create_sudo_submission_object(self,xform_id,attributes_and_values,facility):
    xform = XForm.objects.get(id=xform_id)
    submission = XFormSubmission.objects.create(xform=xform)
    xform.update_submission_from_dict(submission, attributes_and_values)
    subextra = XFormSubmissionExtras.objects.create(submission=submission, facility = facility)
    return submission
    
  @classmethod
  def create_facility(self,facility_name=u'test_facility',dhis2_uuid=u'test_uuid'):
    facility = HealthFacilityBase()
    facility.name = facility_name;
    facility.uuid = dhis2_uuid
    facility.save(cascade_update=False)
    return facility
    
  
  @classmethod
  def create_mappings_for_submission(self,submission,valid_dhis2_ids_list):
    sub_values = XFormSubmissionValue.objects.filter(submission=submission)
    index_dhis2_ids_list = 0
    mappings = valid_dhis2_ids_list.items()
    
    for sub_value in sub_values : 
      attrib_id = sub_value.attribute_id
      dhis2_uid = mappings[index_dhis2_ids_list][0]
      dhis2_combo_id = mappings[index_dhis2_ids_list][1]
      Dhis2_Mtrac_Indicators_Mapping.objects.create(mtrac_id = attrib_id,dhis2_uuid =dhis2_uid ,dhis2_combo_id=dhis2_combo_id)
      index_dhis2_ids_list = (index_dhis2_ids_list+1)%len(valid_dhis2_ids_list)
      
