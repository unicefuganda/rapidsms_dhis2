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
                'period': '201211',
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
class Test_H033B_Reporter(TestCase):
  
  def test_submit_report(self):
  
    with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
      response = H033B_Reporter.submit(TEST_SUBMISSION_DATA)
    assert response.getcode() == 200
    assert response.geturl() == "http://dhis/api/dataValueSets"
    assert response.info().getheader('Content-type') == 'application/xml;charset=UTF-8'
  
    assert self.verify_values(TEST_SUBMISSION_DATA) == True
    
  def verify_values(self, data):
    with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
      query = "?dataSet=V1kJRs8CtW4&period=%s&orgUnit=%s" %(data['period'], data['orgUnit'])
      url = H033B_Reporter.URL + query
      request = urllib2.Request(url, headers=H033B_Reporter.HEADERS)
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
      
  def xtest_iso_time(self):
    dates_iso_string_map = {
      datetime.datetime(2003, 12, 31, 23, 59, 45)   :  '2003-12-31T23:59:45Z' , 
      datetime.datetime(2003, 1 , 31, 23, 59, 45)   :  '2003-01-31T23:59:45Z' , 
      datetime.datetime(2003, 12, 1 , 0 , 0 , 0 )   :  '2003-12-01T00:00:00Z' , 
      datetime.datetime(2003, 2 , 2 , 0 , 0 , 0 )   :  '2003-02-02T00:00:00Z' , 
      datetime.datetime(2003, 12, 31, 23, 59, 59)   :  '2003-12-31T23:59:59Z' , 
  
    }
    
    for date in dates_iso_string_map : 
      print dates_iso_string_map[date] , H033B_Reporter.get_utc_time_iso8601(date)
      self.assertEquals(dates_iso_string_map[date] , H033B_Reporter.get_utc_time_iso8601(date))
  
  def test_get_data_values_for_submission(self):
    submission_value = MagicMock()
    submission_value.attribute_id = 345
    submission_value.value = 22
    
    Dhis2_Mtrac_Indicators_Mapping.objects.create(mtrac_id=submission_value.attribute_id, dhis2_uuid= u'test_uuid',dhis2_combo_id=u'test_combo_id')    
    data =  H033B_Reporter.get_data_values_for_submission(submission_value)
  
    self.assertEquals(data['dataElement'], u'test_uuid')
    self.assertEquals(data['value'],22)
    self.assertEquals(data['categoryOptionCombo'], u'test_combo_id')
    
  def test_generate_xml_report(self):
    rendered_xml  = H033B_Reporter.generate_xml_report(TEST_SUBMISSION_DATA)
    expected_xml = u'<dataValueSet xmlns="http://dhis2.org/schema/dxf/2.0" dataSet="V1kJRs8CtW4" completeDate="2012-11-11T00:00:00Z" period="201211" orgUnit="6VeE8JrylXn">\
                        <dataValue dataElement="U7cokRIptxu"  categoryOptionCombo= "gGhClrV5odI" value="100" />\
                        <dataValue dataElement="mdIPCPfqXaJ" categoryOptionCombo= "gGhClrV5odI" value="99" />\
                      </dataValueSet>'

    rendered_xml =self.temp_fix_remove_whitespaces(rendered_xml)
    expected_xml =self.temp_fix_remove_whitespaces(expected_xml)
    self.assertEquals(rendered_xml,expected_xml)
    
  def temp_fix_remove_whitespaces(self,str):
    return str.replace(' ','').replace('\n', '')
    
