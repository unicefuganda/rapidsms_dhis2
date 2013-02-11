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
        self.fetcher = Dhis2_Fetch_Health_Indicators(97)
    # 
    # def test_get_hmis033b_dataset(self):
    #    with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
    #         obj = self.fetcher.fetch(JSON_EXTENSION, URLS['test_dataset_url'])
    #         self.assertIsNotNone(obj)
    # 
    # def test_clean_indicator_names_from_dhis2(self):
    #     self.assertEqual(self.fetcher.clean_indicator_names_from_dhis2('Bubukwanga - WEP    '), 'Bubukwanga')
    #     self.assertEqual(self.fetcher.clean_indicator_names_from_dhis2('Bubukwanga (helloo there , remove me)'), 'Bubukwanga')
    #     self.assertEqual(self.fetcher.clean_indicator_names_from_dhis2('Bubukwanga - WEP  (asdasdasd ) '), 'Bubukwanga')
    #     self.assertEqual(self.fetcher.clean_indicator_names_from_dhis2('Bubukwanga  (asdasdasd) - WEP '), 'Bubukwanga')
    #     self.assertEqual(self.fetcher.clean_indicator_names_from_dhis2('(asdasdasd) - WEP '), 'asdasdasd')
    #     self.assertEqual(self.fetcher.clean_indicator_names_from_dhis2(' (asdasdasd) '), 'asdasdasd')
    # 
    # def test_compare_strings(self):
    #     self.assertEqual(self.fetcher.compare_strings('Bubukwanga', 'Bubukwanga'), 100)
    #     self.assertEqual(self.fetcher.compare_strings('Bubukwanga', 'Bundibugyo'), 50)
    #     self.assertEqual(self.fetcher.compare_strings('a', 'b'), 0)
    # 
    # def test_get_indicators_names_match_level(self):
    #     self.assertTrue(self.fetcher.get_indicators_names_match_level("Adverse Events Following Immunization Cases - WEP","Adverse Events Following Immunization Cases")==100)
    #     self.assertTrue(self.fetcher.get_indicators_names_match_level("some name - WEP","soome name")>90)
    # 
    # 
    # def test_find_matching_indicator_from_mtrack(self):
    #     test_dhis2_name  = u'Adverse Events Following Immunization Cases - WEP'
    #     expected = u'Adverse Events Following Immunization cases'
    #     matching_mtrack= self.fetcher.find_matching_indicator_from_mtrack(test_dhis2_name)
    #     self.assertEquals(matching_mtrack.id , 360)
    #    
    # 
    # def test_find_matching_indicator_from_mtrack(self):
    #     test_dhis2_name  = u'I DONT EXIST IN MTRACK...YEAHHHH - WEP'
    #     self.assertEquals(self.fetcher.find_matching_indicator_from_mtrack(test_dhis2_name),None)
    # 
    # def test_find_matches_and_update_mapping_table(self):
    #     Dhis2_Mtrac_Indicators_Mapping.objects.all().delete()
    #     disease = {"name":u"Malaria Cases - WEP", "id": u"fclvwNhzu7d", "href": u"http://dhis/api/dataElements/fclvwNhzu7d", "combo_id":u"92DkrSOchnL" }
    #     self.fetcher.find_matches_and_update_mapping_table(disease)
    #     record = Dhis2_Mtrac_Indicators_Mapping.objects.filter(dhis2_uuid='fclvwNhzu7d')
    #     self.assertIsNotNone(record)
    #     self.assertEquals(len(record), 1)
    #     record = record[0]
    #     self.assertEquals( record.dhis2_name, disease['name'])
    #     self.assertEquals( record.dhis2_uuid, disease['id'])
    #     self.assertEquals( record.dhis2_url, disease['href'])
    #     self.assertEquals( record.dhis2_combo_id, disease['combo_id'])
    #     self.assertEquals( record.mtrac_id, Attribute.objects.get(slug='cases_ma'))
    #     
    # def xtest_sync_indicators_group(self):
    #     indicator = disease = {"name":u"Malaria Cases - WEP", "id": u"fclvwNhzu7d", "href": u"http://dhis/api/dataElements/fclvwNhzu7d", "combo_id":u"92DkrSOchnL" }
    #     # mtrack_indicator = find_matching_indicator_from_mtrack()
    #     
    #     record = Dhis2_Mtrac_Indicators_Mapping.objects.all()
    #     test_indicators_list = [
    #         'Suspected Malaria Cases',
    #         'RDT Tested Cases',
    #         'RDT Positve Cases',
    #         'Microscopy Tested Cases',
    #         'Microscopy Positive Cases',
    #         'Positve Cases Under 5 Years',
    #         'Positive Cases 5+ Years' ]
    #     for test_indicator_name in test_indicators_list : 
    #         self.assertIsNotNone(Dhis2_Mtrac_Indicators_Mapping.objects.filetr(dhis2_name = test_indicator_name))
    # 
    # def test_get_indicator_combo_option_id_default(self):
    #     category_combo_url = 'http://dhis/api/categoryCombos/92DkrSOchnL'        
    #     with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
    #         self.assertEqual(self.fetcher.get_indicator_combo_option_id(category_combo_url), 'gGhClrV5odI')
    # 
    # def test_get_indicator_combo_option_non_default(self):
    #     category_combo_url = 'http://dhis/api/categoryCombos/7O1Zh4rJoIn'        
    #     with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
    #         self.assertIsNone(self.fetcher.get_indicator_combo_option_id(category_combo_url) )
    #         
    #         
    # def test_get_category_combos_from_combo_category_option(self):
    #     category_combo_url = 'http://dhis/api/categoryCombos/7O1Zh4rJoIn'        
    #     with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
    #         indicators = self.fetcher.get_category_combos_from_combo_category_option(category_combo_url) 
    #         
    #         self.assertEquals(len(indicators),12)
    #         for indicator in indicators : 
    #              self.assertIsNotNone(indicator['combo_id'])
    #              self.assertIsNotNone(indicator['name'])
    #              self.assertIsNotNone(indicator['href'])
    # 
    # def test_get_combo_id_from_indicator(self):
    #     url = 'http://dhis/api/dataElements/fTwT8uX9Uto'       
    #     with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
    #         combo_id = self.fetcher.get_combo_id_from_indicator(url) 
    #         self.assertEquals(combo_id,'gGhClrV5odI')
    #         
    # def test_update_mappings_table_with_default_indicator(self):
    #     disease_url = 'http://dhis/api/dataElements/fTwT8uX9Uto'        
    #     with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
    #         self.fetcher.update_mappings_table(disease_url)
    #         record = Dhis2_Mtrac_Indicators_Mapping.objects.filter(dhis2_url= disease_url)
    #         self.assertEqual(len(record), 1)
    #         record=record[0]
    #         self.assertEqual(record.dhis2_name, 'Adverse Events Following Immunization Cases - WEP')
    #         self.assertEqual(record.dhis2_uuid, 'fTwT8uX9Uto')
    #         self.assertEqual(record.dhis2_combo_id, 'gGhClrV5odI')
    #         self.assertEqual(record.mtrac_id, Attribute.objects.get(slug='cases_ae'))

    def test_update_mappings_table_with_non_default_indicator(self):
        indicator_url = 'http://dhis/api/dataElements/KPmTI3TGwZw'        
        with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
            self.fetcher.update_mappings_table(indicator_url)
            record = Dhis2_Mtrac_Indicators_Mapping.objects.filter(dhis2_uuid= 'KPmTI3TGwZw')
            self.assertEqual(len(record), 7)
            
            record_mtrac =list( [a_record.mtrac_id.id for a_record in record])
            expected_list = list[Attribute.objects.get(slug='test_sm').id,
                             Attribute.objects.get(slug='test_rdt').id, 
                             Attribute.objects.get(slug='test_rdp').id,
                             Attribute.objects.get(slug='test_mtc').id,
                             Attribute.objects.get(slug='test_mtp').id,
                             Attribute.objects.get(slug='test_pcc').id,
                             Attribute.objects.get(slug='test_pcy').id ])

            print record_mtrac
            print Attribute.objects.get(slug='test_sm').id
            self.assertListEqual(record_mtrac , expected_list)
        