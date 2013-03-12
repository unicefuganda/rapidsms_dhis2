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
SOME_VALID_DHIS_ELEMENT_ID_AND_COMBO =  {
  u'NoJfAIcxjSY' : u'gGhClrV5odI',
  u'OMxmmYvvLai' : u'gGhClrV5odI',
  u'w3mO7SZdbb8' : u'gGhClrV5odI',
  u'UKYPpKnSBK4' : u'gGhClrV5odI',
  u'fclvwNhzu7d' : u'gGhClrV5odI',
  u'JTc25LIvtQb' : u'gGhClrV5odI',
  u'tjTnFJ1QdVz' : u'gGhClrV5odI',
  u'6WfcY8YJ73L' : u'BrX1bohix6a',
  u'6WfcY8YJ73L' : u'drJyZS90kYV',
  u'6WfcY8YJ73L' : u'JFoz3bCuOZf',
  u'BX2PYPKm8F9' : u'gGhClrV5odI',
  u'r3xIBQaeLsT' : u'gGhClrV5odI',
  u'IkI01xB7RIi' : u'gGhClrV5odI',
  u'JxUexqKeXtZ' : u'gGhClrV5odI',
}


class Submissions_Test_Helper(object):
  
    
  @classmethod  
  def create_submission_object(self,xform_id,attributes_and_values,facility):
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
  def create_attribute_mappings_for_submission(self,submission,valid_dhis2_ids_list=SOME_VALID_DHIS_ELEMENT_ID_AND_COMBO):
    sub_values = XFormSubmissionValue.objects.filter(submission=submission)
    index_dhis2_ids_list = 0
    mappings = valid_dhis2_ids_list.items()
    
    for sub_value in sub_values : 
      dhis2_uid = mappings[index_dhis2_ids_list][0]
      dhis2_combo_id = mappings[index_dhis2_ids_list][1]
      
      Dhis2_Mtrac_Indicators_Mapping.objects.create(eav_attribute = sub_value.attribute,dhis2_uuid =dhis2_uid ,dhis2_combo_id=dhis2_combo_id)
      index_dhis2_ids_list = (index_dhis2_ids_list+1)%len(valid_dhis2_ids_list)
      
      
