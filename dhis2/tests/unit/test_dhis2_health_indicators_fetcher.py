from django.test import TestCase
import sys, os, vcr, dhis2 
from dhis2.dhis2_match import *
from dhis2.models import Dhis2_Mtrac_Indicators_Mapping
import json
from mock import *

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
            obj = self.fetcher.fetch(JSON_EXTENSION, URLS['test_dataset_url'])
            self.assertIsNotNone(obj)

    def test_clean_indicator_names_from_dhis2(self):
        self.assertEqual(self.fetcher.clean_indicator_names_from_dhis2('Bubukwanga - WEP    '), 'Bubukwanga')
        self.assertEqual(self.fetcher.clean_indicator_names_from_dhis2('Bubukwanga (helloo there , remove me)'), 'Bubukwanga')
        self.assertEqual(self.fetcher.clean_indicator_names_from_dhis2('Bubukwanga - WEP  (asdasdasd ) '), 'Bubukwanga')
        self.assertEqual(self.fetcher.clean_indicator_names_from_dhis2('Bubukwanga  (asdasdasd) - WEP '), 'Bubukwanga')

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
        matching_mtrack= self.fetcher.find_matching_indicator_from_mtrack(test_dhis2_name)
        self.assertEquals(matching_mtrack.id , 360)
   

    def test_find_matching_indicator_from_mtrack(self):
        test_dhis2_name  = u'I DONT EXIST IN MTRACK...YEAHHHH - WEP'
        self.assertEquals(self.fetcher.find_matching_indicator_from_mtrack(test_dhis2_name),None)
    
    def test_find_matches_and_update_mapping_table(self):
        Dhis2_Mtrac_Indicators_Mapping.objects.all().delete()
        disease_json = json.loads('{"name":"Malaria Cases - WEP", "type":"int", "id": "fclvwNhzu7d", "href": "http://dhis/api/dataElements/fclvwNhzu7d", "categoryCombo":{"id":"92DkrSOchnL"} }')
        self.fetcher.find_matches_and_update_mapping_table(disease_json)
        record = Dhis2_Mtrac_Indicators_Mapping.objects.filter(dhis2_uuid='fclvwNhzu7d')
        self.assertIsNotNone(record)
        self.assertEquals(len(record), 1)
        record = record[0]
        self.assertEquals( record.dhis2_name, disease_json['name'])
        self.assertEquals( record.dhis2_type, disease_json['type'])
        self.assertEquals( record.dhis2_url, disease_json['href'])
        self.assertEquals( record.dhis2_combo_id, disease_json['categoryCombo']['id'])
        
    def test_sync_indicators_group(self):
        self.fetcher.sync_disease_indicators(DHIS2_CONNECTION_CONFIG['urls']['categoryComboUrlBase']+'/uh4pYNd1CSv')
        record = Dhis2_Mtrac_Indicators_Mapping.objects.all()
        test_indicators_list = [
            'Suspected Malaria Cases',
            'RDT Tested Cases',
            'RDT Positve Cases',
            'Microscopy Tested Cases',
            'Microscopy Positive Cases',
            'Positve Cases Under 5 Years',
            'Positive Cases 5+ Years' ]
        for test_indicator_name in test_indicators_list : 
            self.assertIsNotNone(Dhis2_Mtrac_Indicators_Mapping.objects.filetr(dhis2_name = test_indicator_name))
        
        
