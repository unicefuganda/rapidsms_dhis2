from django.test import TestCase
from dhis2.h033b_reporter import *
from lxml import etree
import urllib2, vcr, os, dhis2, sys
import datetime
from dhis2.models import Dhis2_Mtrac_Indicators_Mapping
from mock import *

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
      print dates_iso_string_map[date] , self.h033b_reporter.get_utc_time_iso8601(date)
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
  
  def test_log_submission_finished_with_success(self):
    self.h033b_reporter.log_submission_started()
  
    self.h033b_reporter.log_submission_finished_with_success( 
      submission_count=100,
      status= Dhis2_Reports_Report_Task_Log.SUCCESS,
      description='Submitted succesfully to dhis2')
    
    log_record_fetched = Dhis2_Reports_Report_Task_Log.objects.all()[0]
    self.assertEquals(log_record_fetched.number_of_submissions , 100)
    self.assertEquals(log_record_fetched.description , 'Submitted succesfully to dhis2')
    self.assertEquals(log_record_fetched.status , Dhis2_Reports_Report_Task_Log.SUCCESS)
    self.assertIsNotNone(log_record_fetched.time_finished)
  
  def test_parse_submission_response_with_errror(self):
    result= self.h033b_reporter.parse_submission_response(ERROR_XML_RESPONSE)
    self.assertEquals(result['ignored'],1 )
    self.assertEquals(result['imported'],1)
    self.assertEquals(result['updated'],1 )
    self.assertIsNotNone(result['error'])
  
  def test_parse_submission_response_no_error(self):
    result = self.h033b_reporter.parse_submission_response(SUCCESS_XML_RESPONSE)
    self.assertEquals(result['ignored'],0 )
    self.assertEquals(result['imported'],3)
    self.assertEquals(result['updated'],2 )

    self.assertIsNone(result['error'])

