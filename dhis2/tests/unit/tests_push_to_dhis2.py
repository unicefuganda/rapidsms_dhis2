from django.test import TestCase
from dhis2.h033b_reporter import *
from lxml import etree
import urllib2, vcr, os, dhis2, sys
import datetime

FIXTURES = os.path.abspath(dhis2.__path__[0]) + "/tests/fixtures/cassettes/"

class Test_H033B_Reporter(TestCase):

  def test_submit_report(self):
    submit_data = { 'orgUnit': "6VeE8JrylXn",
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
    with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
      response = H033B_Reporter.submit(submit_data)
    assert response.getcode() == 200
    assert response.geturl() == "http://dhis/api/dataValueSets"
    assert response.info().getheader('Content-type') == 'application/xml;charset=UTF-8'

    assert self.verify_values(submit_data) == True
    
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

  def xtest_generate_period_id_for_week(self):
    start_dates = { 
      datetime.datetime(2013, 01, 01, 23, 59, 59) : '2004W10'
      }
    
    expected  = ''
    
  def Xtest_prepare_report_for_submission_to_dhis(self):
    test_data = {
        'completeDate': datetime.datetime(2012, 10, 23, 6, 28, 39, 891455),
        'dataValues': [{358: 100}],
        'orgUnit': 1419 
        }
    expected  = { 
      'orgUnit': "6VeE8JrylXn",
      'completeDate': "2012-11-11T00:00:00Z",
      'period': '201211',
      'dataValues': [
                      {
                        'dataElement': 'U7cokRIptxu',
                        'value': 100,
                        'categoryOptionCombo' : 'gGhClrV5odI'
                      }
                    ]
              }
              
    report_data = H033B_Reporter.prepare_report_for_submission_to_dhis(test_data)    
    self.assertDictEqual(report_data['orgUnit'], expected['orgUnit'])
    self.assertDictEqual(report_data['completeDate'], expected['completeDate'])    
    self.assertDictEqual(report_data['period'], expected['period'])
    self.assertDictEqual(report_data['dataValues'][0]['dataElement'], expected['dataValues'][0]['dataElement'])    
    self.assertDictEqual(report_data['dataValues'][0]['value'], expected['dataValues'][0]['value'])    
    self.assertDictEqual(report_data['dataValues'][0]['categoryOptionCombo'], expected['dataValues'][0]['categoryOptionCombo'])    
    