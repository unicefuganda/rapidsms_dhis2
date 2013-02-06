from django.test import TestCase
import sys, os, vcr, dhis2 
from dhis2.dhis2_match import Dhis2_Fetch_Health_Indicators
from dhis2.models import Dhis2_Mtrac_Indicators_Mapping

FRED_CONFIG = {"url": "http://dhis/api/", "username": "api", "password": "P@ssw0rd"}
FIXTURES = os.path.abspath(dhis2.__path__[0]) + "/tests/fixtures/cassettes/"

URLS = {
    'test_dataset_url'  : FRED_CONFIG['url'] + 'dataSets/V1kJRs8CtW4',
    'test_dataset_id'   : 'V1kJRs8CtW4'
}

JSON_EXTENSION = '.json'

class Test_Dhis2_Fetch_Health_Indicators(TestCase):

    def setUp(self):
        self.fetcher = Dhis2_Fetch_Health_Indicators(99)
    
    def test_get_hmis033b_dataset(self):
       with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            obj = self.fetcher.get_dataset(JSON_EXTENSION, URLS['test_dataset_url'])
            self.assertIsNotNone(obj)

    def test_compare_strings(self):
        self.assertEqual(self.fetcher.compare_strings('Bubukwanga', 'Bubukwanga'), 100)
        self.assertEqual(self.fetcher.compare_strings('Bubukwanga', 'Bundibugyo'), 50)
        self.assertEqual(self.fetcher.compare_strings('a', 'b'), 0)

    def test_get_indicators_names_match_level(self):
        self.assertTrue(self.fetcher.get_indicators_names_match_level("Adverse Events Following Immunization Cases - WEP","Adverse Events Following Immunization Cases")==100)
        self.assertTrue(self.fetcher.get_indicators_names_match_level("some name - WEP","soome name")>90)

    def test_find_matching_indicator_from_mtrack(self):
        test_dhis2_name  = u'Adverse Events Following Immunization Cases - WEP'
        expected = u'Adverse Events Following Immunization cases'
        id, name, slug = self.fetcher.find_matching_indicator_from_mtrack(test_dhis2_name)

        self.assertEquals(id , 360)
        self.assertEquals(name , expected)
        self.assertEquals(slug , 'cases_ae')
    

    def test_find_matching_indicator_from_mtrack(self):
        test_dhis2_name  = u'I DONT EXIST IN MTRACK...YEAHHHH - WEP'
        self.assertEquals(self.fetcher.find_matching_indicator_from_mtrack(test_dhis2_name),None)
    
    
    def test_find_matches_and_update_mapping_table(self):
        self.assertEquals(len(Dhis2_Mtrac_Indicators_Mapping.objects.all()),0)
        self.fetcher.find_matches_and_update_mapping_table()
    

# if __name__ == '__main__':
#   suite = unittest.TestLoader().loadTestsFromTestCase(TestDHIS2_Fetch_Web_API)
#   unittest.TextTestRunner(verbosity=2).run(suite)