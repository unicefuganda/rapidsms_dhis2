import urllib2
import base64
import json
import re
import psycopg2
import psycopg2.extras
import Levenshtein
from eav.models import Attribute
from models import Dhis2_Mtrac_Indicators_Mapping

DHIS2_CONNECTION_CONFIG = {
    'urls': {
        'diseases': 'http://dhis/api/dataSets/V1kJRs8CtW4',
        'categoryComboUrlBase' : 'http://dhis/api/categoryCombos/'
    },
    "combo_ids" : {
        'diseases': '92DkrSOchnL',
        'act':  '7O1Zh4rJoIn',
        'treat':'uh4pYNd1CSv',
        'test': 'IohHeDqzJk1'
        },
    'user': 'sekiskylink',
    'password': '123Congse',
    'content-type': 'json'
}

DHIS2_HEALTH_INDICATORS_NAME_ERASE_SUFFIX_REGEXES = ['\- WEP',r'\(.+\)']

class Dhis2_Fetch_Health_Indicators(object):
    def __init__(self, match_threshold):
        self.match_threshold = match_threshold
        auth = base64.b64encode("%(user)s:%(password)s" % DHIS2_CONNECTION_CONFIG)
        self.HEADERS = {
            'Content-type': 'application/json; charset="UTF-8"',
            'Authorization': 'Basic '+auth
        }

        self.BASE_URL = DHIS2_CONNECTION_CONFIG['urls']

    def fetch(self, extension, url = None, query = None):
        url = (url or self.BASE_URL['diseases']) + extension
        if query:
            url += "?" + query

        request = urllib2.Request(url, headers=self.HEADERS)
        response = urllib2.urlopen(request)
        return json.loads(response.read())

    def clean_indicator_names_from_dhis2(self , dhis2_indicator_name):
        for reg_ex in DHIS2_HEALTH_INDICATORS_NAME_ERASE_SUFFIX_REGEXES : 
            dhis2_indicator_name =  re.sub(reg_ex, '', dhis2_indicator_name).strip()
        return dhis2_indicator_name


    def compare_strings(self, some_string, another_string):
        ratio = Levenshtein.ratio(some_string.strip().lower(), another_string.strip().lower())
        return round(ratio * 100)

    def get_indicators_names_match_level(self, dhis2_name, mtrack_name):
        return self.compare_strings(self.clean_indicator_names_from_dhis2(dhis2_name), mtrack_name) 

    def find_matching_indicator_from_mtrack(self, dhis2_indicator_name):
        min_match_level = self.match_threshold 
        all_mtrack_indicators = Attribute.objects.all()
        matching_indicator = None

        for mtrack_indicator in all_mtrack_indicators : 
            match_level = self.get_indicators_names_match_level(dhis2_indicator_name, mtrack_indicator.name)
            if match_level >= min_match_level : 
                matching_indicator = mtrack_indicator
                min_match_level = match_level

        if matching_indicator : 
            return   matching_indicator
    
    def find_matches_and_update_mapping_table(self, dhis2_json):
        mtrack_indicator_id  = self.find_matching_indicator_from_mtrack(dhis2_json['name'])
        self.update_dhis2_mapping_db(dhis2_json, mtrack_indicator_id )
        
    def update_dhis2_mapping_db (self, dhis2_json, mtrack_indicator):
        Dhis2_Mtrac_Indicators_Mapping.objects.create(
            mtrac_id = mtrack_indicator, 
            dhis2_uuid = dhis2_json['id'],
            dhis2_name  = dhis2_json['name'],
            dhis2_url  = dhis2_json['href'],
            dhis2_combo_id = dhis2_json['categoryCombo']['id'] )
            
    def sync_disease_indicators(self):
        indicators_group_json = self.fetch('.json',DHIS2_CONNECTION_CONFIG['urls']['diseases'])['dataElements']
        
        for indicator in indicators_group_json :
            self.find_matches_and_update_mapping_table(indicator)
        
        
    
