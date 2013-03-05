from django.test import TestCase
from dhis2.h033b_reporter import *
from lxml import etree
import urllib2, vcr, os, dhis2, sys
import datetime
from dhis2.models import Dhis2_Mtrac_Indicators_Mapping
from mock import *
from mtrack.models import XFormSubmissionExtras
from healthmodels.models.HealthFacility import HealthFacilityBase
from rapidsms_xforms.models import XFormSubmissionValue,XForm,XFormSubmission,XFormField
from dhis2.tests.test_helper import Submissions_Test_Helper
from healthmodels.models.HealthFacility import HealthFacilityBase

A_VALID_DHIS2_UUID = u'6VeE8JrylXn'
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
ACTS_XFORM_ID = 55
VITAMIN_A_XFORM_ID= 63

FIXTURES = os.path.abspath(dhis2.__path__[0]) + "/tests/fixtures/cassettes/"
TEST_SUBMISSION_DATA = { 'orgUnit': "6VeE8JrylXn",
                'completeDate': "2012-11-11T00:00:00Z",
                'period': '2012W45',
                'dataValues': [
                                {
                                  'dataElement': 'U7cokRIptxu',
                                  'value': 100,
                                  'categoryOptionCombo' : 'gGhClrV5odI'
                                },
                                {
                                  'dataElement': 'mdIPCPfqXaJ',
                                  'value': 99,
                                  'categoryOptionCombo' :'gGhClrV5odI'
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

class Test_H033B_Reporter(TestCase):
  def setUp(self):
    self.h033b_reporter = H033B_Reporter()
  
  def test_submit(self):
    with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
      result = self.h033b_reporter.submit(TEST_SUBMISSION_DATA)
    accepted_attributes_values = result['updated'] + result['imported']
    self.assertEquals(accepted_attributes_values,2)
    self.assertIsNone(result['error'])
  
  
  def verify_values(self, data):
    with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
      query = "?dataSet=V1kJRs8CtW4&period=%s&orgUnit=%s" %(data['period'], data['orgUnit'])
      url = self.h033b_reporter.URL + query
      request = urllib2.Request(url, headers=self.h033b_reporter.HEADERS)
      response = urllib2.urlopen(request)
      xml = etree.fromstring(response.read())
      rows = []
      for i in xml.iterchildren():
        rows.append(i)
  
      assert len(rows) == len(data['dataValues'])
  
      for key, datavalue in enumerate(data['dataValues']):
        row = rows[key].values()
        assert datavalue['dataElement'] == row[0]
        assert str(datavalue['value']) == row[4]
  
      return True
  
    for date in dates_iso_string_map :
      self.assertEquals(dates_iso_string_map[date] , self.h033b_reporter.get_utc_time_iso8601(date))
  
  def test_get_data_values_for_submission(self):
    submission_value = MagicMock()
    submission_value.attribute_id = 345
    submission_value.value = 22
  
    Dhis2_Mtrac_Indicators_Mapping.objects.create(mtrac_id=submission_value.attribute_id, dhis2_uuid= u'test_uuid',dhis2_combo_id=u'test_combo_id')
    data =  self.h033b_reporter.get_data_values_for_submission(submission_value)
  
    self.assertEquals(data['dataElement'], u'test_uuid')
    self.assertEquals(data['value'],22)
    self.assertEquals(data['categoryOptionCombo'], u'test_combo_id')
  
  def test_generate_xml_report(self):
    rendered_xml  = self.h033b_reporter.generate_xml_report(TEST_SUBMISSION_DATA)
    expected_xml = u'<dataValueSet xmlns="http://dhis2.org/schema/dxf/2.0" dataSet="V1kJRs8CtW4" completeDate="2012-11-11T00:00:00Z" period="2012W45" orgUnit="6VeE8JrylXn">\
                        <dataValue dataElement="U7cokRIptxu"  categoryOptionCombo= "gGhClrV5odI" value="100" />\
                        <dataValue dataElement="mdIPCPfqXaJ" categoryOptionCombo= "gGhClrV5odI" value="99" />\
                      </dataValueSet>'
  
    rendered_xml =self.temp_fix_remove_whitespaces(rendered_xml)
    expected_xml =self.temp_fix_remove_whitespaces(expected_xml)
    self.assertEquals(rendered_xml,expected_xml)
  
  def temp_fix_remove_whitespaces(self,str):
    return str.replace(' ','').replace('\n', '')
  
  def test_iso_time(self):
    dates_iso_string_map = {
      datetime.datetime(2003, 12, 31, 23, 59, 45)   :  '2003-12-31T23:59:45Z' ,
      datetime.datetime(2003, 1 , 31, 23, 59, 45)   :  '2003-01-31T23:59:45Z' ,
      datetime.datetime(2003, 12, 1 , 0 , 0 , 0 )   :  '2003-12-01T00:00:00Z' ,
      datetime.datetime(2003, 2 , 2 , 0 , 0 , 0 )   :  '2003-02-02T00:00:00Z' ,
      datetime.datetime(2003, 12, 31, 23, 59, 59)   :  '2003-12-31T23:59:59Z' ,
    }
  
    for date in dates_iso_string_map :
      self.assertEquals(dates_iso_string_map[date] , self.h033b_reporter.get_utc_time_iso8601(date))
  
  def test_get_week_period_id_for_sunday(self):
     periods_test_args = {
       datetime.datetime(2013, 1, 4, 0, 0, 0)        : u'2013W1' ,
       datetime.datetime(2010, 1, 3, 23, 59, 45)     : u'2010W1'  ,
       datetime.datetime(2010, 1 , 10, 23, 59, 45)   : u'2010W2'  ,
       datetime.datetime(2010, 2, 7 , 0 , 0 , 0 )    : u'2010W6' ,
       datetime.datetime(2010, 3 , 7 , 0 , 0 , 0 )   : u'2010W10'  ,
       datetime.datetime(2010, 12, 26, 23, 59, 59)   : u'2010W52',
       datetime.datetime(2012, 1, 1, 23, 59, 59)     : u'2012W1'
      }
  
     for date in periods_test_args :
       self.assertEquals(periods_test_args[date] , self.h033b_reporter.get_week_period_id_for_sunday(date))
  
  def test_get_last_sunday_for_day(self):
      days = {
        datetime.datetime(2010, 1, 7, 0, 0, 0)     : datetime.datetime(2010, 1, 3, 0, 0, 0) ,
        datetime.datetime(2010, 1 , 13, 0, 0, 0)   :  datetime.datetime(2010, 1, 10, 0, 0, 0)   ,
        datetime.datetime(2010, 2, 9 , 0 , 0 , 0 )    :  datetime.datetime(2010, 2, 7, 0, 0, 0)  ,
        datetime.datetime(2010, 3 , 8 , 0 , 0 , 0 )   :  datetime.datetime(2010, 3, 7, 0, 0, 0)   ,
        datetime.datetime(2010, 12, 31, 0, 0, 0)   : datetime.datetime(2010, 12, 26, 0, 0, 0)  ,
        datetime.datetime(2012, 1, 7, 0, 0, 0)     :  datetime.datetime(2012, 1, 1, 0, 0, 0)
       }
  
      for date in days :
        self.assertEquals(days[date] , self.h033b_reporter.get_last_sunday(date))
  
  def test_get_period_id_from_submissions_on_given_dates(self):
      from_dates = {
        datetime.datetime(2010, 1, 7, 0, 0, 0)        : u'2010W1',
        datetime.datetime(2010, 1 , 13, 0, 0, 0)      : u'2010W2'  ,
        datetime.datetime(2010, 2, 9 , 0 , 0 , 0 )    : u'2010W6' ,
        datetime.datetime(2010, 3 , 8 , 0 , 0 , 0 )   : u'2010W10'  ,
        datetime.datetime(2010, 12, 31, 0, 0, 0)      : u'2010W52' ,
        datetime.datetime(2012, 1, 7, 0, 0, 0)        : u'2012W1'
       }
  
      for date in from_dates:
        self.assertEquals(from_dates[date] , self.h033b_reporter.get_period_id_for_submission(date))
  
  def test_log_submission_started(self):
    self.h033b_reporter.log_submission_started()
    log_record = Dhis2_Reports_Report_Task_Log.objects.all()[0]
    time = datetime.datetime.now()
    self.assertEquals(log_record.status , Dhis2_Reports_Report_Task_Log.RUNNING)
    self.assertIsNotNone(time)
  
  def test_log_submission_finished(self):
    self.h033b_reporter.log_submission_started()
  
    self.h033b_reporter.log_submission_finished(
      submission_count=100,
      status= Dhis2_Reports_Report_Task_Log.SUCCESS,
      description='Submitted succesfully to dhis2')
  
    log_record_fetched = Dhis2_Reports_Report_Task_Log.objects.all()[0]
    self.assertEquals(log_record_fetched.number_of_submissions , 100)
    self.assertEquals(log_record_fetched.description , 'Submitted succesfully to dhis2')
    self.assertEquals(log_record_fetched.status , Dhis2_Reports_Report_Task_Log.SUCCESS)
    self.assertIsNotNone(log_record_fetched.time_finished)
  
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
  
  def test_get_reports_data_for_submission_for_valid_data(self):
      submission_extras_obj = XFormSubmissionExtras()
      test_uuid = u'TEST_UUID'
      cdate  = datetime.datetime(2003, 1, 1, 23, 59, 45)
      test_facility = HealthFacilityBase(uuid = test_uuid)
  
      submission_extras_obj.cdate= cdate
      submission_extras_obj.facility =test_facility
      data = self.h033b_reporter.get_reports_data_for_submission([submission_extras_obj])
  
      self.assertEquals(data['orgUnit'],test_uuid)
      self.assertEquals(data['completeDate'],u'2003-01-01T23:59:45Z')
      self.assertEquals(data['period'],u'2002W52')
  
  def test_set_data_values_from_submission_value(self):
      value1={
          'attribute_id': 362 ,
          'value'       : 9989 ,
          'dhis2_uuid'  : u'test_dhis2_uuid_1',
          'categoryOptionCombo' : u'XCV'
      }
      submission_values = self.get_submission_values_and_mappings([value1])
      data = {}
  
      self.h033b_reporter.set_data_values_from_submission_value(data,submission_values)
  
      self.assertEquals(data['dataValues'][0]['dataElement'] ,u'test_dhis2_uuid_1' )
      self.assertEquals(data['dataValues'][0]['value'] ,9989 )
      self.assertEquals(data['dataValues'][0]['categoryOptionCombo'] ,u'XCV' )
  
  
  def get_submission_values_and_mappings(self,key_values_mapping_list):
      submission_values = []
      for kvm in key_values_mapping_list :
        submission_value = XFormSubmissionValue()
        submission_value.attribute_id = kvm['attribute_id']
        submission_value.value = kvm['value']
        Dhis2_Mtrac_Indicators_Mapping.objects.create(mtrac_id=kvm['attribute_id'],dhis2_uuid=kvm['dhis2_uuid'],dhis2_combo_id=kvm['categoryOptionCombo'])
        submission_values.append(submission_value)
      return submission_values
      
  def test_xformsubmissionextras_does_not_exist(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {u'epd': 53,
     u'eps': 62,
     u'fpd': 71,
     u'fps': 80,
     u'spd': 17,
     u'sps': 26,
     u'tpd': 35,
     u'tps': 44}
    submission = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility = None)     
    subextra = XFormSubmissionExtras.objects.filter(submission=submission).delete()
    Submissions_Test_Helper.xformsubmissionextras_does_not_exist(submission.id)
    
    
    
  def test_xformsubmission_no_valid_hmis_indicator_exists(step):
    xform_id = VITAMIN_A_XFORM_ID
    attributes_and_values = {
     u'male1': 44,
     u'female1': 45,
     u'male2': 46,
     u'female2': 47
     }
    facility= Submissions_Test_Helper.create_facility()
    submission = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility= facility)    
    Submissions_Test_Helper.no_valid_hms_indicator_exists(submission.id)
    
  def test_dhis2_returns_error(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {u'epd': 53,
     u'eps': 62,
     u'fpd': 71,
     u'fps': 80,
     u'spd': 17,
     u'sps': 26,
     u'tpd': 35,
     u'tps': 44}
    
    facility= Submissions_Test_Helper.create_facility(dhis2_uuid = A_VALID_DHIS2_UUID)
    submission = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility = facility)     
    Submissions_Test_Helper.create_mappings_for_submission(submission,SOME_VALID_DHIS_ELEMENT_ID_AND_COMBO)
    Submissions_Test_Helper.dhis2_returns_error(submission.id)
    
  def test_set_data_values_from_submission_value(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {u'epd': 53,
     u'eps': 62,
     }
    facility_uuid = 'TEST_FACILITY_UUID'
    
    xfrom_field_mappings = [
      {
        'x_form_field_command_id' : u'epd',
        'dhis2_uuid'  :u'dhis2uuid_1',
        'combo_id'    : u'combo_id1'
      },
      {
        'x_form_field_command_id' : u'eps',
        'dhis2_uuid'  :u'dhis2uuid_2',
        'combo_id'    : u'comboid2'
      }
    ]
  
    
    for xfrom_field_mapping in xfrom_field_mappings :
      mtrac_id  = XFormField.objects.filter(command=xfrom_field_mapping['x_form_field_command_id'])[0].attribute_ptr_id
      Dhis2_Mtrac_Indicators_Mapping.objects.create(
        mtrac_id = mtrac_id,
        dhis2_uuid = xfrom_field_mapping['dhis2_uuid'] ,
        dhis2_combo_id= xfrom_field_mapping['combo_id']
      )
      
    
    facility= Submissions_Test_Helper.create_facility(dhis2_uuid = A_VALID_DHIS2_UUID)
    facility.uuid = facility_uuid
    facility.save(cascade_update=False)
    
    submission = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility = facility)
      
    submission_time  =  datetime.datetime(2013, 1, 4, 0, 0, 0) 
    xsub_extra = XFormSubmissionExtras.objects.filter(submission=submission)[0]
    xsub_extra.cdate = submission_time
    xsub_extra.save()    
    
    data  =  self.h033b_reporter.get_reports_data_for_submission(XFormSubmissionExtras.objects.filter(submission=submission))
    submission_values = XFormSubmissionValue.objects.filter(submission=submission)
    self.h033b_reporter.set_data_values_from_submission_value(data,submission_values)
    
    self.assertEquals(data['orgUnit'],facility_uuid)
    self.assertEquals(data['completeDate'] , u'2013-01-04T00:00:00Z')
    self.assertEquals(data['period'],u'2012W53')
    self.assertEquals(len(data['dataValues']),2 )
    
    self.assertEquals(data['dataValues'][0]['dataElement'] , xfrom_field_mappings[0]['dhis2_uuid'] )
    self.assertEquals(data['dataValues'][0]['categoryOptionCombo'] ,  xfrom_field_mappings[0]['combo_id'] )
    self.assertEquals(data['dataValues'][0]['value'] ,  53)
    
    self.assertEquals(data['dataValues'][1]['dataElement'] , xfrom_field_mappings[1]['dhis2_uuid']  )
    self.assertEquals(data['dataValues'][1]['categoryOptionCombo'] ,  xfrom_field_mappings[1]['combo_id'] )
    self.assertEquals(data['dataValues'][1]['value'] ,  62)
    
    
  def test_get_submissions_in_date_range(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {u'epd': 53,
     u'eps': 62,
     }
    submissions_count = 13
    from_date = datetime.datetime(2011, 12, 18, 00, 00, 00)
    to_date = datetime.datetime(2011, 12, 19, 23, 59, 59)
    
    submission = XFormSubmission.objects.all().delete()
    facility= Submissions_Test_Helper.create_facility()
    
    for x in range(submissions_count) : 
      facility= Submissions_Test_Helper.create_facility(facility_name=u'test_facility'+str(x),dhis2_uuid=u'test_uuid2'+str(x))
      
      submission = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
        attributes_and_values=attributes_and_values,facility = facility)
        
      submission.created = from_date + timedelta(seconds = ((to_date-from_date).seconds + x/submissions_count))
      submission.save()
    
    
  
    submissions_in_period  = self.h033b_reporter.get_submissions_in_date_range(from_date,to_date)
    self.assertEquals(len(submissions_in_period) , submissions_count)
  
  def test_get_submissions_in_date_range_has_no_error_records(self):
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {}
    submissions_count = 13
    error_submissions = 3
    from_date = datetime.datetime(2011, 12, 18, 00, 00, 00)
    to_date = datetime.datetime(2011, 12, 19, 23, 59, 59)
    
    XFormSubmission.objects.all().delete()
    
    for x in range(submissions_count) : 
      facility= Submissions_Test_Helper.create_facility(facility_name=u'test_facility'+str(x),dhis2_uuid=u'test_uuid2'+str(x))
      
      submission = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
        attributes_and_values=attributes_and_values,facility = facility)
      submission.created = from_date + timedelta(seconds = ((to_date-from_date).seconds + x/submissions_count))
      
      if error_submissions > x :
        submission.has_errors = True
      submission.save()
    
    submissions_in_period  = self.h033b_reporter.get_submissions_in_date_range(from_date,to_date)
    self.assertEquals(len(submissions_in_period) , submissions_count-error_submissions)
  
  def test_remove_duplicate_reports_missing_extras(self):
    h033b_reporter = H033B_Reporter()
    
    xform_id = VITAMIN_A_XFORM_ID
    attributes_and_values = {
     u'male1': 44,
     u'female1': 45,
     u'male2': 46,
     u'female2': 47
     }
     
    
    XFormSubmission.objects.all().delete()
     
    facility1= Submissions_Test_Helper.create_facility()
    facility2= Submissions_Test_Helper.create_facility(facility_name=u'test_facility2',dhis2_uuid=u'test_uuid2')
    
    good_submission = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility= facility1)   
    
    bad_submission = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility= facility2)    
    XFormSubmissionExtras.objects.filter(submission=bad_submission).delete()    
      
    submissions_list = h033b_reporter.remove_duplicate_and_invalid_reports(XFormSubmission.objects.all())
    
    self.assertEquals([good_submission], submissions_list)
  
    
  
  def test_remove_duplicate_reports(self):
    h033b_reporter = H033B_Reporter()
    
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
    
    XFormSubmission.objects.all().delete()
     
    facility= Submissions_Test_Helper.create_facility()
    
    x1 = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility= facility)   
    
    x2 =Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility= facility)    
    
    latest_submission1 = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility= facility)    
    
  
    facility2= Submissions_Test_Helper.create_facility(facility_name=u'test_facility2',dhis2_uuid=u'test_uuid2')
    Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
       attributes_and_values=attributes_and_values,facility= facility2)   
     
  
    latest_submission2 = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
       attributes_and_values=attributes_and_values,facility= facility2)
  
    Submissions_Test_Helper.create_sudo_submission_object(xform_id=ACTS_XFORM_ID,
          attributes_and_values=attributes_and_values2,facility= facility2)
          
    latest_submission3 = Submissions_Test_Helper.create_sudo_submission_object(xform_id=ACTS_XFORM_ID,
      attributes_and_values=attributes_and_values2,facility= facility2)    
    
    facility3= Submissions_Test_Helper.create_facility(facility_name=u'test_facility3',dhis2_uuid=u'test_uuid3')
    
    bad1 = Submissions_Test_Helper.create_sudo_submission_object(xform_id=ACTS_XFORM_ID,
      attributes_and_values=attributes_and_values2,facility= facility2)
    bad2 = Submissions_Test_Helper.create_sudo_submission_object(xform_id=ACTS_XFORM_ID,
        attributes_and_values=attributes_and_values2,facility= facility3)
    XFormSubmissionExtras.objects.filter(submission=bad1).delete()
    XFormSubmissionExtras.objects.filter(submission=bad2).delete()
        
    latest_submission4 = Submissions_Test_Helper.create_sudo_submission_object(xform_id=ACTS_XFORM_ID,
      attributes_and_values=attributes_and_values2,facility= facility3)
    
    submissions_list = h033b_reporter.remove_duplicate_and_invalid_reports(XFormSubmission.objects.all())
    
    assert x1.created < x2.created
    assert latest_submission1.created >  x2.created
    
    self.assertEquals(len(submissions_list),4  )
    self.assertTrue(latest_submission1 in submissions_list)
    self.assertTrue(latest_submission2 in submissions_list)
    self.assertTrue(latest_submission3 in submissions_list)
    self.assertTrue(latest_submission4 in submissions_list)
    
    
  
  def test_get_submissions_in_date_range_has_extras_but_no_facility_id(self):
    h033b_reporter = H033B_Reporter()
    
    xform_id = VITAMIN_A_XFORM_ID
    attributes_and_values = {
     u'male1': 44,
     u'female1': 45,
     u'male2': 46,
     u'female2': 47
     }
     
    
    XFormSubmission.objects.all().delete()
     
    facility1= Submissions_Test_Helper.create_facility()
    facility2= Submissions_Test_Helper.create_facility(facility_name=u'test_facility2',dhis2_uuid=u'test_uuid2')
    
    good_submission = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility= facility1)   
    
    bad_submission = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
      attributes_and_values=attributes_and_values,facility= facility2)    
    bad_extra  = XFormSubmissionExtras.objects.filter(submission=bad_submission)[0]
    bad_extra.facility = None
    bad_extra.save()
        
      
    submissions_list = h033b_reporter.remove_duplicate_and_invalid_reports(XFormSubmission.objects.all())
    
    self.assertEquals([good_submission], submissions_list)
    
  
  def test_weekly_submissions(self):
    h033b_reporter = H033B_Reporter()
    
    xform_id = ACTS_XFORM_ID
    attributes_and_values = {
      u'epd': 53,
         u'eps': 62,
    }
    some_valid_facility_uuids = [
      u'6VeE8JrylXn',
      u'xYZq8eBXMrD',
      u'nBDPw7Qhd7r'
    ] 
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

    submissions_count = 3
    from_date = datetime.datetime(2013, 1, 21, 00, 00, 00)
    to_date = datetime.datetime(2013, 1, 24, 23, 59, 59)
    
    XFormSubmission.objects.all().delete()
    Dhis2_Reports_Report_Task_Log.objects.all().delete()
    Dhis2_Reports_Submissions_Log.objects.all().delete()
    
    for xfrom_field_mapping in xfrom_field_mappings :
      mtrac_id  = XFormField.objects.filter(command=xfrom_field_mapping['x_form_field_command_id'])[0].attribute_ptr_id
      Dhis2_Mtrac_Indicators_Mapping.objects.create(
        mtrac_id = mtrac_id,
        dhis2_uuid = xfrom_field_mapping['dhis2_uuid'] ,
        dhis2_combo_id= xfrom_field_mapping['combo_id']
      )
      
    
    for x in range(submissions_count) : 
      facility= Submissions_Test_Helper.create_facility(facility_name=u'test_facility'+str(x),dhis2_uuid=some_valid_facility_uuids[x%len(some_valid_facility_uuids )])
      
      submission = Submissions_Test_Helper.create_sudo_submission_object(xform_id=xform_id,
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
      

