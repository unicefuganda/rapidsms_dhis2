import settings
import vcr, os, sys
import dhis2
from datetime import timedelta,datetime
from xml.dom.minidom import parseString
from dhis2.h033b_reporter import *
from django.test import TestCase
from dhis2.tests.test_helper import Submissions_Test_Helper
from rapidsms_xforms.models import XForm, XFormField , XFormSubmission,  XFormSubmissionValue
from mtrack.models import XFormSubmissionExtras 
from eav.models import Attribute
from dhis2.models import Dhis2_Mtrac_Indicators_Mapping ,Dhis2_Reports_Report_Task_Log,Dhis2_Reports_Submissions_Log
from mock import *


A_VALID_DHIS2_UUID = u'3b8a12cd-b844-4d87-ab9b-86308af7139a'
TEST_DHIS2_BASE_URL = 'http://ec2-54-242-108-118.compute-1.amazonaws.com'
TEST_DHIS2_USER = 'api'
TEST_DHIS2_PASSWORD = 'Passw0rd'
ACTS_XFORM_ID = 55
VITAMIN_A_XFORM_ID = 63

FIXTURES = os.path.abspath(dhis2.__path__[0]) + u"/tests/fixtures/cassettes/"

TEST_SUBMISSION_DATA = { 'orgUnit': u"3b8a12cd-b844-4d87-ab9b-86308af7139a",
                'completeDate': u"2012-11-11T00:00:00Z",
                'period': u'2012W45',
                "orgUnitIdScheme":u"uuid",
                'dataValues': [
                                {
                                  'dataElement': u'U7cokRIptxu',
                                  'value': 100,
                                  'categoryOptionCombo' : 'gGhClrV5odI'
                                },
                                {
                                  'dataElement': u'mdIPCPfqXaJ',
                                  'value': 99,
                                  'categoryOptionCombo' :u'gGhClrV5odI'
                                }
                              ]
              }
              
ERROR_XML_RESPONSE = '\
<?xml version="1.0" encoding="UTF-8"?>\
<importSummary \
    xmlns="http://dhis2.org/schema/dxf/2.0">\
    <status>SUCCESS</status>\
    <description>Import process completed successfully</description>\
    <dataValueCount imported="1" updated="1" ignored="1"/>\
    <conflicts>\
        <conflict object="OrganisationUnit" value="Must be provided to complete data set"/>\
        <conflict object="OrganisationUnit"/>\
        <conflict object="OrganisationUnit"/>\
    </conflicts>\
</importSummary>'

SUCCESS_XML_RESPONSE = '\
<?xml version="1.0" encoding="UTF-8"?>\
<importSummary \
    xmlns="http://dhis2.org/schema/dxf/2.0">\
    <status>SUCCESS</status>\
    <description>Import process completed successfully</description>\
    <dataValueCount imported="3" updated="2" ignored="0"/>\
    <dataSetComplete>2012-11-11</dataSetComplete>\
</importSummary>'

SOME_VALID_FACILITY_UUIDS = [
  u'3b8a12cd-b844-4d87-ab9b-86308af7139a',
  u'45d81a6f-0060-4c6e-ad28-f7a3d8932904',
  u'2315d1ea-35da-4fdd-99ca-06feab246784'
]

class Test_H033B_Reporter(TestCase):
  
  def setUp(self):
    self.h033b_reporter = H033B_Reporter()
    
  def test_url(self):
    settings.URL = TEST_DHIS2_BASE_URL
    self.assertEquals(self.h033b_reporter.url,TEST_DHIS2_BASE_URL+'/api/dataValueSets')
  
  def test_parse_submission_response_with_errror(self):
    request_xml = 'xx'
    result= self.h033b_reporter.parse_submission_response(ERROR_XML_RESPONSE,request_xml)
    self.assertEquals(result['ignored'],1 )
    self.assertEquals(result['imported'],1)
    self.assertEquals(result['updated'],1 )
    self.assertIsNotNone(result['error'])
    self.assertEquals(result['request_xml'],request_xml)
    
  def test_parse_submission_response_no_error(self):
    request_xml = 'xx'
    result = self.h033b_reporter.parse_submission_response(SUCCESS_XML_RESPONSE,request_xml)
    self.assertEquals(result['ignored'],0 )
    self.assertEquals(result['imported'],3)
    self.assertEquals(result['updated'],2 )
    
    self.assertIsNone(result['error'])
    self.assertEquals(result['request_xml'],request_xml)
    
  def test_generate_xml_report(self):
    rendered_xml  = self.h033b_reporter.generate_xml_report(TEST_SUBMISSION_DATA)                                      
    dom = parseString(rendered_xml)
    dataValueSet   = dom.getElementsByTagName  ('dataValueSet')[0]
    element_data_values  = dom.getElementsByTagName ('dataValue')
    self.assertEquals(dataValueSet.getAttribute('completeDate'),TEST_SUBMISSION_DATA['completeDate'])
    self.assertEquals(dataValueSet.getAttribute('period'),TEST_SUBMISSION_DATA['period'])
    self.assertEquals(dataValueSet.getAttribute('orgUnitIdScheme'),TEST_SUBMISSION_DATA['orgUnitIdScheme'])
    self.assertEquals(dataValueSet.getAttribute('orgUnit'),TEST_SUBMISSION_DATA['orgUnit']) 
    for element_data_value in element_data_values :
      
      data_element = element_data_value.getAttribute('dataElement')
      category_option_combo = element_data_value.getAttribute('categoryOptionCombo')
      value = element_data_value.getAttribute('value')
      data_value = self.__find_element_id_data_values(data_element,TEST_SUBMISSION_DATA['dataValues'])
      
      self.assertEquals(data_element,data_value['dataElement'])
      self.assertEquals(category_option_combo,data_value['categoryOptionCombo'])
      self.assertEquals(int(value),data_value['value'])
      
  def __find_element_id_data_values(self,data_element,data_values):
    for data_value in data_values : 
      if data_value['dataElement'] == data_element  :
        return data_value
        
    assertion_failure_message = "Data element %s not found in %s"%(data_element,data_values)
    raise AssertionError( assertion_failure_message )
    
  def test_submit(self):
    with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
      result = self.h033b_reporter.submit_report(TEST_SUBMISSION_DATA)
    accepted_attributes_values = result['updated'] + result['imported']
    self.assertEquals(accepted_attributes_values,2)
    self.assertIsNone(result['error'])
    
  def test_iso_time(self):
    dates_iso_string_map = {
      datetime(2003, 12, 31, 23, 59, 45)   :  '2003-12-31T23:59:45Z' ,
      datetime(2003, 1 , 31, 23, 59, 45)   :  '2003-01-31T23:59:45Z' ,
      datetime(2003, 12, 1 , 0 , 0 , 0 )   :  '2003-12-01T00:00:00Z' ,
      datetime(2003, 2 , 2 , 0 , 0 , 0 )   :  '2003-02-02T00:00:00Z' ,
      datetime(2003, 12, 31, 23, 59, 59)   :  '2003-12-31T23:59:59Z' ,
    }
    
    for date in dates_iso_string_map :
      self.assertEquals(dates_iso_string_map[date] , self.h033b_reporter.get_utc_time_iso8601(date))

  def test_get_week_period_id_for_sunday(self):
     periods_test_args = {
       datetime(2013, 1, 4, 0, 0, 0)        : u'2013W1' ,
       datetime(2010, 1, 3, 23, 59, 45)     : u'2010W1'  ,
       datetime(2010, 1 , 10, 23, 59, 45)   : u'2010W2'  ,
       datetime(2010, 2, 7 , 0 , 0 , 0 )    : u'2010W6' ,
       datetime(2010, 3 , 7 , 0 , 0 , 0 )   : u'2010W10'  ,
       datetime(2010, 12, 26, 23, 59, 59)   : u'2010W52',
       datetime(2012, 1, 1, 23, 59, 59)     : u'2012W1'
      }

     for date in periods_test_args :
       self.assertEquals(periods_test_args[date] , self.h033b_reporter.get_week_period_id_for_sunday(date))

  def test_get_last_sunday_for_day(self):
      days = {
        datetime(2010, 1, 7, 0, 0, 0)     : datetime(2010, 1, 3, 0, 0, 0) ,
        datetime(2010, 1 , 13, 0, 0, 0)   :  datetime(2010, 1, 10, 0, 0, 0)   ,
        datetime(2010, 2, 9 , 0 , 0 , 0 )    :  datetime(2010, 2, 7, 0, 0, 0)  ,
        datetime(2010, 3 , 8 , 0 , 0 , 0 )   :  datetime(2010, 3, 7, 0, 0, 0)   ,
        datetime(2010, 12, 31, 0, 0, 0)   : datetime(2010, 12, 26, 0, 0, 0)  ,
        datetime(2012, 1, 7, 0, 0, 0)     :  datetime(2012, 1, 1, 0, 0, 0)
       }

      for date in days :
        self.assertEquals(days[date] , self.h033b_reporter.get_last_sunday(date))
  
  def test_get_period_id_from_submissions_on_given_dates(self):
      from_dates = {
        datetime(2010, 1, 7, 0, 0, 0)        : u'2010W1',
        datetime(2010, 1 , 13, 0, 0, 0)      : u'2010W2'  ,
        datetime(2010, 2, 9 , 0 , 0 , 0 )    : u'2010W6' ,
        datetime(2010, 3 , 8 , 0 , 0 , 0 )   : u'2010W10'  ,
        datetime(2010, 12, 31, 0, 0, 0)      : u'2010W52' ,
        datetime(2012, 1, 7, 0, 0, 0)        : u'2012W1'
       }

      for date in from_dates:
        self.assertEquals(from_dates[date] , self.h033b_reporter.get_period_id_for_submission(date))

  def test_get_reports_data_for_submission_with_no_values_to_report(self):
    attributes_and_values = {}
    xform_id = ACTS_XFORM_ID
    facility= Submissions_Test_Helper.create_facility(facility_name=u'facility_xyz',dhis2_uuid='uuid')
    submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
        attributes_and_values=attributes_and_values,facility = facility)
    submission.facility = facility
    self.assertRaises(LookupError, self.h033b_reporter.get_reports_data_for_submission, submission)

  def test_get_reports_data_for_submission(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {u'epd': 53, u'eps': 62, u'fpd': 71}
    
    dhis2_uuis_and_combo_ids= [
     (u'NoJfAIcxjSY' , u'gGhClrV5odI'),
     (u'OMxmmYvvLai' , u'BrX1bohix6a'),
     (u'w3mO7SZdbb8' , u'drJyZS90kYV'),
      ]
     
    self._create_dhis2_indicator_mapping( xform_id = ACTS_XFORM_ID, 
        attributes_and_values = attributes_and_values,
        dhis2_uuis_and_combo_ids= dhis2_uuis_and_combo_ids)

    
    facility = Submissions_Test_Helper.create_facility(facility_name=u'xyz',dhis2_uuid=u'uuid_xxx')    
    submission = self._create_submission(facility = facility, xform_id=xform_id, attributes_and_values=attributes_and_values)  
 
    submission_data = self.h033b_reporter.get_reports_data_for_submission(submission)
    sorter = lambda dataValue : dataValue['dataElement']
    submission_data['dataValues']  = sorted(submission_data['dataValues'],key=sorter)
    
    self.assertEquals(submission_data['dataValues'][0]['dataElement'] , 'NoJfAIcxjSY')
    self.assertEquals(submission_data['dataValues'][0]['value'] ,53 )
    self.assertEquals(submission_data['dataValues'][0]['categoryOptionCombo'] ,u'gGhClrV5odI' )
                                            
    self.assertEquals(submission_data['dataValues'][1]['dataElement'] , 'OMxmmYvvLai')
    self.assertEquals(submission_data['dataValues'][1]['value'] ,62 )
    self.assertEquals(submission_data['dataValues'][1]['categoryOptionCombo'] ,u'BrX1bohix6a' )
                                                
    self.assertEquals(submission_data['dataValues'][2]['dataElement'] , 'w3mO7SZdbb8')
    self.assertEquals(submission_data['dataValues'][2]['value'] ,71 )
    self.assertEquals(submission_data['dataValues'][2]['categoryOptionCombo'] ,u'drJyZS90kYV' )
    
    self.assertEquals(submission_data['orgUnit'], u'uuid_xxx')
    self.assertEquals(submission_data['completeDate'], u'2012-01-07T00:00:00Z')
    self.assertEquals(submission_data['period'], u'2012W1')
    self.assertEquals(submission_data['orgUnitIdScheme'], u'uuid')
    
  def test_missing_corresponding_dhis2_ids_and_or_comboids_generates_no_reports_data_for_submission(self):
    xform_id = ACTS_XFORM_ID
    missing_dhis2_uuis_and_combo_ids= [(u'OMxmmYvvLai' , u'BrX1bohix6a')]
    corresponding_attributes_and_values = { u'eps': 62}
    correct_attributes_and_values = {u'epd': 53, u'eps': 62, u'fpd': 71}

    self._create_dhis2_indicator_mapping( xform_id = ACTS_XFORM_ID, 
        dhis2_uuis_and_combo_ids= missing_dhis2_uuis_and_combo_ids,
        attributes_and_values = corresponding_attributes_and_values)
    
    facility = Submissions_Test_Helper.create_facility(facility_name=u'xyz',dhis2_uuid=u'uuid_xxx')    
    submission = self._create_submission(facility = facility, xform_id=xform_id,
                  attributes_and_values= correct_attributes_and_values)  

    submission_data = self.h033b_reporter.get_reports_data_for_submission(submission)

    self.assertEquals(len(submission_data['dataValues']) , 1)

    self.assertEquals(submission_data['dataValues'][0]['dataElement'] , 'OMxmmYvvLai')
    self.assertEquals(submission_data['dataValues'][0]['value'] ,62 )
    self.assertEquals(submission_data['dataValues'][0]['categoryOptionCombo'] ,u'BrX1bohix6a' )

  @patch('rapidsms_xforms.models.XFormSubmissionValue.objects.filter')
  def test_missing_indicator_values_are_NOT_reported_in_data_for_submission(self, mock_xform_filter):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {u'epd': 53, u'eps': 62, u'fpd': 71}

    dhis2_uuis_and_combo_ids= [
     (u'NoJfAIcxjSY' , u'gGhClrV5odI'),
     (u'OMxmmYvvLai' , u'BrX1bohix6a'),
     (u'w3mO7SZdbb8' , u'drJyZS90kYV'),
      ]

    self._create_dhis2_indicator_mapping( xform_id = ACTS_XFORM_ID, 
        attributes_and_values = attributes_and_values,
        dhis2_uuis_and_combo_ids= dhis2_uuis_and_combo_ids)


    facility = Submissions_Test_Helper.create_facility(facility_name=u'xyz',dhis2_uuid=u'uuid_xxx')    
    submission = self._create_submission(facility = facility, xform_id=xform_id, attributes_and_values=attributes_and_values)  
    
    
    # mocking needed because _create_submission (only used in test not dhis2) automatically clean None submission.value 
    xform = XForm.objects.get(id=xform_id)

    submission_value_epd = MagicMock()
    submission_value_epd.value = None
    submission_value_epd.attribute = XFormField.objects.get(xform=xform, command='epd')
    
    submission_value_eps = MagicMock()
    submission_value_eps.value = None
    submission_value_eps.attribute = XFormField.objects.get(xform=xform, command='eps')
    
    submission_value_fpd = MagicMock()
    submission_value_fpd.value = 71
    submission_value_fpd.attribute = XFormField.objects.get(xform=xform, command='fpd')
    
    mock_xform_filter.return_value = [submission_value_epd, submission_value_eps, submission_value_fpd]

    submission_data = self.h033b_reporter.get_reports_data_for_submission(submission)
    
    self.assertEquals(len(submission_data['dataValues']) , 1)
    
    self.assertEquals(submission_data['dataValues'][0]['dataElement'] , 'w3mO7SZdbb8')
    self.assertEquals(submission_data['dataValues'][0]['value'] ,71 )
    self.assertEquals(submission_data['dataValues'][0]['categoryOptionCombo'] ,u'drJyZS90kYV' )
  
  def _create_dhis2_indicator_mapping(self,   xform_id = ACTS_XFORM_ID, 
    attributes_and_values = {u'epd': 53, u'eps': 62, u'fpd': 71}, 
    dhis2_uuis_and_combo_ids= [
     (u'NoJfAIcxjSY' , u'gGhClrV5odI'),
     (u'OMxmmYvvLai' , u'BrX1bohix6a'),
     (u'w3mO7SZdbb8' , u'drJyZS90kYV'),
      ] ):

    xform_fields_commands = sorted (attributes_and_values.keys())

    for index in range(len(xform_fields_commands)) : 
      dhis2_uid = dhis2_uuis_and_combo_ids[index][0]
      dhis2_combo_id = dhis2_uuis_and_combo_ids[index][1]
      attribute = XFormField.objects.get(command=xform_fields_commands[index]).attribute_ptr

      Dhis2_Mtrac_Indicators_Mapping.objects.create( 
        eav_attribute = attribute,
        dhis2_uuid =dhis2_uid ,
        dhis2_combo_id=dhis2_combo_id
      )

  def _create_submission(self, facility,
    created = datetime(2012, 1, 7, 0, 0, 0), 
    xform_id = ACTS_XFORM_ID,
    attributes_and_values = {u'epd': 53, u'eps': 62, u'fpd': 71}
    ):
    
    submission = Submissions_Test_Helper.create_submission_object(
      xform_id=xform_id,
      attributes_and_values=attributes_and_values,
      facility = facility
    )

    submission.created = created
    submission.save()   

    submission.facility = facility

    return submission

  
  def test_get_submissions_in_date_range(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {}

    
    from_date = datetime(2011, 12, 18, 00, 00, 00)
    to_date = datetime(2011, 12, 19, 23, 59, 59)
    
    XFormSubmission.objects.all().delete()
    
    facility = Submissions_Test_Helper.create_facility(facility_name=u'test_facility1',dhis2_uuid=u'test_uuid1')   
    
    submission1 = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
        attributes_and_values=attributes_and_values,facility = facility)
    
    facility_2 = Submissions_Test_Helper.create_facility(facility_name=u'test_facility2',dhis2_uuid=u'test_uuid2')   
    
    submission2 = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
            attributes_and_values=attributes_and_values,facility = facility_2)
        
    submission1.created = from_date + timedelta(seconds = 1)
    submission2.created = to_date - timedelta(seconds =1)
    submission1.save()
    submission2.save()
    
    submissions_in_period  = self.h033b_reporter.get_submissions_in_date_range(from_date,to_date)
    sort_by_id = lambda submission : submission.id
    
    submissions_in_period = sorted(list(submissions_in_period),key=sort_by_id)
    
    self.assertEquals(len(submissions_in_period) , 2)
    
    if submission1.id > submission2.id :
      submission2,submission1  =  submission1,submission2
    
    self.assertEquals(submissions_in_period[0].id , submission1.id)
    self.assertEquals(submissions_in_period[1].id , submission2.id)
    
  def test_get_submissions_in_date_range_for_submissions_has_errors_True(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {}

    from_date = datetime(2011, 12, 18, 00, 00, 00)
    to_date = datetime(2011, 12, 19, 23, 59, 59)

    facility = Submissions_Test_Helper.create_facility(facility_name=u'test_facility1',dhis2_uuid=u'test_uuid1')   

    submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
       attributes_and_values=attributes_and_values,facility = facility)
    submission.created = from_date + timedelta(seconds = 1)
    submission.has_errors = True
    submission.save()

    submissions_in_period  = self.h033b_reporter.get_submissions_in_date_range(from_date,to_date)
    self.assertEquals(len(submissions_in_period) , 0)
    
    
  def test_get_submissions_in_date_range_for_no_submission_extra(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {}

    from_date = datetime(2011, 12, 18, 00, 00, 00)
    to_date = datetime(2011, 12, 19, 23, 59, 59)

    facility = Submissions_Test_Helper.create_facility(facility_name=u'test_facility1',dhis2_uuid=u'test_uuid1')   

    submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
       attributes_and_values=attributes_and_values,facility = facility)
    submission.created = from_date + timedelta(seconds = 1)
    submission.save()
    
    XFormSubmissionExtras.objects.get(submission=submission).delete()
    submissions_in_period  = self.h033b_reporter.get_submissions_in_date_range(from_date,to_date)
    self.assertEquals(len(submissions_in_period) , 0)
  
  def test_get_submissions_in_date_range_for_missing_facility(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {}

    from_date = datetime(2011, 12, 18, 00, 00, 00)
    to_date = datetime(2011, 12, 19, 23, 59, 59)

    facility = Submissions_Test_Helper.create_facility(facility_name=u'test_facility1', dhis2_uuid=u'test_uuid1')   

    submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
       attributes_and_values=attributes_and_values,facility = facility)
    submission.created = from_date + timedelta(seconds = 1)
    submission.save()
    
    xtra = XFormSubmissionExtras.objects.get(submission=submission)
    xtra.facility = None
    xtra.save()
    
    submissions_in_period  = self.h033b_reporter.get_submissions_in_date_range(from_date,to_date)

    self.assertEquals(len(submissions_in_period) , 0)
         

  
  def test_get_submissions_in_date_range_for_reported_submissions(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {}
    h033b_reporter = H033B_Reporter()

    from_date = datetime(2011, 12, 18, 00, 00, 00)
    to_date = datetime(2011, 12, 19, 23, 59, 59)

    facility = Submissions_Test_Helper.create_facility(facility_name=u'test_facility1',dhis2_uuid=u'test_uuid1')   

    submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
       attributes_and_values=attributes_and_values,facility = facility)
       
    submission.created = from_date + timedelta(seconds = 1)
    submission.save()
    h033b_reporter.log_submission_started()
    report_submissions_log = Dhis2_Reports_Submissions_Log.objects.create(
      task_id = h033b_reporter.current_task,
      submission_id = submission.id,
      reported_xml = 'crap', 
      result = Dhis2_Reports_Report_Task_Log.SUCCESS,
      description ='No Description'
    )
    
    submissions_in_period  = h033b_reporter.get_submissions_in_date_range(from_date,to_date)

    self.assertEquals(len(submissions_in_period) , 0)
    
  def test_get_submissions_in_date_range_returns_no_submission_while_latest_submission_is_already_reported_to_dhis2(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {}
    h033b_reporter = H033B_Reporter()

    from_date = datetime(2011, 12, 18, 00, 00, 00)
    to_date = datetime(2011, 12, 19, 23, 59, 59)

    XFormSubmission.objects.all().delete()

    facility = Submissions_Test_Helper.create_facility(facility_name=u'test_facility1',dhis2_uuid=u'test_uuid1')   

    old_submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
        attributes_and_values=attributes_and_values,facility = facility)

    latest_submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
            attributes_and_values=attributes_and_values,facility = facility)

    old_submission.created = from_date + timedelta(seconds = 1)
    latest_submission.created = to_date - timedelta(seconds =1)
    old_submission.save()
    latest_submission.save()

    h033b_reporter.log_submission_started()
    
    report_submissions_log = Dhis2_Reports_Submissions_Log.objects.create(
      task_id = h033b_reporter.current_task,
      submission_id = latest_submission.id,
      reported_xml = 'crap', 
      result = Dhis2_Reports_Report_Task_Log.SUCCESS,
      description ='No Description'
    )
    
    submissions_in_period  = h033b_reporter.get_submissions_in_date_range(from_date,to_date)

    self.assertEquals(len(submissions_in_period) , 0)

  def test_get_submissions_in_date_range_returns_submissions_created_after_last_submission_report(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {}
    h033b_reporter = H033B_Reporter()

    from_date = datetime(2011, 12, 18, 00, 00, 00)
    to_date = datetime(2011, 12, 19, 23, 59, 59)

    XFormSubmission.objects.all().delete()

    facility = Submissions_Test_Helper.create_facility(facility_name=u'test_facility1',dhis2_uuid=u'test_uuid1')   

    old_submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
        attributes_and_values=attributes_and_values,facility = facility)

    reported_submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
            attributes_and_values=attributes_and_values,facility = facility)

    old_submission.created = from_date + timedelta(seconds = 1)
    reported_submission.created = from_date + timedelta(seconds = 5)
    old_submission.save()
    reported_submission.save()

    h033b_reporter.log_submission_started()

    report_submissions_log = Dhis2_Reports_Submissions_Log.objects.create(
      task_id = h033b_reporter.current_task,
      submission_id = reported_submission.id,
      reported_xml = 'crap', 
      result = Dhis2_Reports_Report_Task_Log.SUCCESS,
      description ='No Description'
    )
    
    new_submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
            attributes_and_values=attributes_and_values,facility = facility)
    new_submission.created = to_date - timedelta(seconds =1)        
    new_submission.save()
    

    submissions_in_period  = h033b_reporter.get_submissions_in_date_range(from_date,to_date)

    self.assertEquals(len(submissions_in_period) , 1)  
    self.assertEquals(submissions_in_period[0].id, new_submission.id)  
         
  def test_remove_duplicate_reports(self):
    xform_id = VITAMIN_A_XFORM_ID
    attributes_and_values = {
     u'male1': 44,
     u'female1': 45,
     u'male2': 46,
     u'female2': 47
     }

    attributes_and_values2 = {
      u'epd': 53,
         u'eps': 62,
         }
    from_date  = datetime.now()
    
    XFormSubmission.objects.all().delete()

    facility= Submissions_Test_Helper.create_facility()

    Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility= facility)   

    Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility= facility)    

    latest_submission1 = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility= facility)    


    facility2= Submissions_Test_Helper.create_facility(facility_name=u'test_facility2',dhis2_uuid=u'test_uuid2')
    
    Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
       attributes_and_values=attributes_and_values,facility= facility2)   


    latest_submission2 = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
       attributes_and_values=attributes_and_values,facility= facility2)

    Submissions_Test_Helper.create_submission_object(xform_id=ACTS_XFORM_ID,
          attributes_and_values=attributes_and_values2,facility= facility2)

    latest_submission3 = Submissions_Test_Helper.create_submission_object(xform_id=ACTS_XFORM_ID,
      attributes_and_values=attributes_and_values2,facility= facility2)    

    facility3= Submissions_Test_Helper.create_facility(facility_name=u'test_facility3',dhis2_uuid=u'test_uuid3')

    latest_submission4 = Submissions_Test_Helper.create_submission_object(xform_id=ACTS_XFORM_ID,
      attributes_and_values=attributes_and_values2,facility= facility3)
      
    to_date = datetime.now()
    
    submissions_list  = self.h033b_reporter.get_submissions_in_date_range(from_date,to_date)

    self.assertEquals(len(submissions_list), 4)
    self.assertTrue(latest_submission1 in submissions_list)
    self.assertTrue(latest_submission2 in submissions_list)
    self.assertTrue(latest_submission3 in submissions_list)
    self.assertTrue(latest_submission4 in submissions_list)
    
  def test_log_submission_started(self):
    before = datetime.now()
    self.h033b_reporter.log_submission_started()
    after = datetime.now()
    
    log_record = Dhis2_Reports_Report_Task_Log.objects.all()[0]
    self.assertEquals(log_record.status , Dhis2_Reports_Report_Task_Log.RUNNING)
    self.assertTrue(before < log_record.time_started )
    self.assertTrue(after > log_record.time_started )
    

  def test_log_submission_finished(self):
    Dhis2_Reports_Report_Task_Log.objects.all().delete()
    self.h033b_reporter.log_submission_started()
    
    self.h033b_reporter.log_submission_finished(
      submission_count=100,
      status= Dhis2_Reports_Report_Task_Log.SUCCESS,
      description='Submitted succesfully to dhis2')

    log_record_fetched = Dhis2_Reports_Report_Task_Log.objects.all()[0]
    self.assertEquals(log_record_fetched.number_of_submissions , 100)
    self.assertEquals(log_record_fetched.description , 'Submitted succesfully to dhis2')
    self.assertEquals(log_record_fetched.status , Dhis2_Reports_Report_Task_Log.SUCCESS)
    
  def test_no_valid_hms_indicator_exists(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {u'epd': 53,
     u'tps': 44}
     
    h033b_reporter = H033B_Reporter()
    h033b_reporter.log_submission_started()
    facility= Submissions_Test_Helper.create_facility(dhis2_uuid = A_VALID_DHIS2_UUID)
    submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility = facility)   

    submission.facility = facility
    submission.save()
    
    h033b_reporter.submit_report_and_log_result(submission)
    log = Dhis2_Reports_Submissions_Log.objects.get(submission_id=submission.id)
    
    self.assertIsNone(log.reported_xml)
    self.assertEquals(log.task_id,h033b_reporter.current_task)
    self.assertEquals(log.result,Dhis2_Reports_Submissions_Log.INVALID_SUBMISSION_DATA)
    self.assertIsNotNone(log.description)
      

  def test_dhis2_returns_error(self):
    self.h033b_reporter = H033B_Reporter()
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {u'epd': 53,
     u'tps': 44}

    cdate = datetime(2013,1,1,1,1,1)
    facility= Submissions_Test_Helper.create_facility(dhis2_uuid = 'CRAP_UUID_TO_CAUSE_ERROR')
    submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility = facility)   

    submission.created = cdate
    submission.facility = facility
    submission.save()

    Submissions_Test_Helper.create_attribute_mappings_for_submission(submission)
    self.h033b_reporter.log_submission_started()
  
    with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
      result = self.h033b_reporter.submit_report_and_log_result(submission)

    log = Dhis2_Reports_Submissions_Log.objects.get(task_id=self.h033b_reporter.current_task)
    
    
    self.assertIsNotNone(log.reported_xml)
    self.assertEquals(log.task_id,self.h033b_reporter.current_task)
    self.assertEquals(log.submission_id,submission.id)
    self.assertEquals(log.result,Dhis2_Reports_Submissions_Log.ERROR)
    self.assertIsNotNone(log.description  )  

  def test_doesnt_log_xml_for_success_submissions(self):
    h033b_reporter = H033B_Reporter()
    submission = self.create_submission()
    h033b_reporter.log_submission_started()
    
    mock_send = lambda data : h033b_reporter.parse_submission_response(SUCCESS_XML_RESPONSE,'request xml')
    h033b_reporter.submit_report = mock_send
    
    result = h033b_reporter.submit_report_and_log_result(submission)

    log = Dhis2_Reports_Submissions_Log.objects.get(task_id=h033b_reporter.current_task)


    self.assertIsNone(log.reported_xml)
    self.assertEquals(log.submission_id,submission.id)
    self.assertEquals(log.result,Dhis2_Reports_Submissions_Log.SUCCESS)


        
  def test_http_response_contains_error_is_logged(self):
    h033b_reporter = H033B_Reporter()
    submission = self.create_submission()
    h033b_reporter.log_submission_started()
    DUMMY_INTEGER  = 11111111
    result = {'error': 'some http response error', 
              'updated': DUMMY_INTEGER,
               'imported': DUMMY_INTEGER,
               'request_xml':'some xml to be logged'}
    
    mock_submit = lambda data : result
    h033b_reporter.submit_report = mock_submit
    
    h033b_reporter.submit_report_and_log_result(submission)
    log  = Dhis2_Reports_Submissions_Log.objects.get(submission_id = submission.id)
    
    self.assertEquals(log.result, Dhis2_Reports_Submissions_Log.ERROR )
    self.assertEquals(log.description, result['error'])
    self.assertEquals(log.reported_xml, result['request_xml'])
    
  def test_http_response_rejects_all_indicators_is_logged(self):
    h033b_reporter = H033B_Reporter()
    submission = self.create_submission()
    h033b_reporter.log_submission_started()
    NUMBER_OF_INDICATOR_ACCEPTED  = 0
    result = {'error': None,
              'updated': NUMBER_OF_INDICATOR_ACCEPTED,
               'imported': NUMBER_OF_INDICATOR_ACCEPTED,
               'request_xml':None}

    mock_submit = lambda data : result
    h033b_reporter.submit_report = mock_submit

    h033b_reporter.submit_report_and_log_result(submission)
    log  = Dhis2_Reports_Submissions_Log.objects.get(submission_id = submission.id)

    self.assertEquals(log.result, Dhis2_Reports_Submissions_Log.ERROR )
    self.assertEquals(log.description, ERROR_MESSAGE_ALL_VALUES_IGNORED)
    self.assertEquals(log.reported_xml, result['request_xml'])

  def test_http_response_accepts_no_indicators_is_logged(self):
    h033b_reporter = H033B_Reporter()
    submission = self.create_submission()
    h033b_reporter.log_submission_started()
    SOME_POSITIVE_NUMBER  = 1
    INDICATORS_IGNORED  = 1
    
    result = {'error': None,
              'updated': SOME_POSITIVE_NUMBER,
               'imported': SOME_POSITIVE_NUMBER,
               'ignored': INDICATORS_IGNORED,
               'request_xml':None}

    mock_submit = lambda data : result
    h033b_reporter.submit_report = mock_submit

    h033b_reporter.submit_report_and_log_result(submission)
    log  = Dhis2_Reports_Submissions_Log.objects.get(submission_id = submission.id)

    self.assertEquals(log.result, Dhis2_Reports_Submissions_Log.SOME_ATTRIBUTES_IGNORED )
    self.assertEquals(log.description,ERROR_MESSAGE_SOME_VALUES_IGNORED )
    self.assertEquals(log.reported_xml, result['request_xml'])
  
  def test_http_response_rejects_some_indicators_is_logged(self):
    h033b_reporter = H033B_Reporter()
    submission = self.create_submission()
    h033b_reporter.log_submission_started()
    SOME_POSITIVE_NUMBER  = 1
    INDICATORS_IGNORED  = 1

    result = {'error': None,
              'updated': SOME_POSITIVE_NUMBER,
               'imported': SOME_POSITIVE_NUMBER,
               'ignored': INDICATORS_IGNORED,
               'request_xml':None}

    mock_submit = lambda data : result
    h033b_reporter.submit_report = mock_submit

    h033b_reporter.submit_report_and_log_result(submission)
    log  = Dhis2_Reports_Submissions_Log.objects.get(submission_id = submission.id)

    self.assertEquals(log.result, Dhis2_Reports_Submissions_Log.SOME_ATTRIBUTES_IGNORED )
    self.assertEquals(log.description,ERROR_MESSAGE_SOME_VALUES_IGNORED )
    self.assertEquals(log.reported_xml, result['request_xml'])
    
    
  
  def test_http_unrecognized_format_response_is_logged(self):
    h033b_reporter = H033B_Reporter()
    submission = self.create_submission()
    h033b_reporter.log_submission_started()
    SOME_POSITIVE_NUMBER  = 1
    INDICATORS_IGNORED  = 1

    unrecognized_response = 'CRAPPPP'

    mock_submit = lambda data : h033b_reporter.parse_submission_response(unrecognized_response,'request xml')
    h033b_reporter.submit_report = mock_submit

    h033b_reporter.submit_report_and_log_result(submission)
    log  = Dhis2_Reports_Submissions_Log.objects.get(submission_id = submission.id)

    self.assertEquals(log.result, Dhis2_Reports_Submissions_Log.ERROR )
    self.assertTrue(ERROR_MESSAGE_UNEXPECTED_RESPONSE_FROM_DHIS2 in log.description, )
    self.assertEquals(log.reported_xml, 'request xml')  
    

  def test_weekly_submissions(self,submissions_count=3,delete_old_submissions=True):
    h033b_reporter = H033B_Reporter()
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {
      u'epd': 53,
         u'eps': 62,
    }

    xfrom_field_mappings = [
      {
        'x_form_field_command_id' : u'epd',
        'dhis2_uuid'  :u'NoJfAIcxjSY',
        'combo_id'    : u'gGhClrV5odI'
      },
      {
        'x_form_field_command_id' : u'eps',
        'dhis2_uuid'  :u'OMxmmYvvLai',
        'combo_id'    : u'gGhClrV5odI'
      }
    ]

    from_date = datetime(2013, 1, 21, 00, 00, 00)
    to_date = datetime(2013, 1, 24, 23, 59, 59)

    if delete_old_submissions : 
      XFormSubmission.objects.all().delete()
      Dhis2_Reports_Report_Task_Log.objects.all().delete()
      Dhis2_Reports_Submissions_Log.objects.all().delete()

    for xfrom_field_mapping in xfrom_field_mappings :
      mtrac_id  = XFormField.objects.filter(command=xfrom_field_mapping['x_form_field_command_id'])[0].attribute_ptr_id
      eav_attribute = Attribute.objects.get(id=mtrac_id)

      Dhis2_Mtrac_Indicators_Mapping.objects.create(
        eav_attribute = eav_attribute,
        dhis2_uuid = xfrom_field_mapping['dhis2_uuid'] ,
        dhis2_combo_id= xfrom_field_mapping['combo_id']
      )

    for x in range(submissions_count) : 
      facility= Submissions_Test_Helper.create_facility(facility_name=u'test_facility'+str(x),dhis2_uuid=SOME_VALID_FACILITY_UUIDS[x%len(SOME_VALID_FACILITY_UUIDS )])

      submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
        attributes_and_values=attributes_and_values,facility = facility)
      submission.created = from_date + timedelta(seconds = ((to_date-from_date).seconds + x/submissions_count))
      xtras = XFormSubmissionExtras.objects.filter(submission=submission)[0]
      xtras.cdate = submission.created
      xtras.save()
      submission.save()

    with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
      h033b_reporter.initiate_weekly_submissions(to_date)

    log_record_for_task = h033b_reporter.current_task
    log_record_for_submissions =  Dhis2_Reports_Submissions_Log.objects.all()

    self.assertEquals(len(Dhis2_Reports_Report_Task_Log.objects.all()),1)
    self.assertEquals(len(Dhis2_Reports_Submissions_Log.objects.all()),3)
    self.assertEquals(log_record_for_task.number_of_submissions , submissions_count)
    self.assertEquals(log_record_for_task.status , Dhis2_Reports_Report_Task_Log.SUCCESS)

    for log_record_for_submission in log_record_for_submissions : 
      self.assertEquals(log_record_for_submission.result,Dhis2_Reports_Report_Task_Log.SUCCESS)

  def create_submission(self, xform_id=ACTS_XFORM_ID,   attributes_and_values = {u'epd': 53,u'tps': 44},created = datetime(2013,1,1,1,1,1), create_attribute_mappings = True):
    facility= Submissions_Test_Helper.create_facility(dhis2_uuid = A_VALID_DHIS2_UUID)
    submission = Submissions_Test_Helper.create_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility = facility)   

    submission.created = created
    submission.facility = facility
    submission.save()
    
    if create_attribute_mappings:
      Submissions_Test_Helper.create_attribute_mappings_for_submission(submission)
  
    return submission