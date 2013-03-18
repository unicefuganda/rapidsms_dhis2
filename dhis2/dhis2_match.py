import urllib2
import base64
import json
import re
import psycopg2
import psycopg2.extras
import Levenshtein
from eav.models import Attribute
from models import Dhis2_Mtrac_Indicators_Mapping
from settings import *
# http://dhis/api/dataElements/.json

DHIS2_CONNECTION_CONFIG = {
    'urls': {
        'diseases': DHIS2_BASE_URL+'/api/dataSets/V1kJRs8CtW4',
        'categoryComboUrlBase' : DHIS2_BASE_URL+'/api/categoryCombos/'
    },
    "combo_ids" : {
        'diseases': '92DkrSOchnL',
        'act':  '6WfcY8YJ73L',
        'treat':'uh4pYNd1CSv',
        'test': 'IohHeDqzJk1'
        },
    'user': DHIS2_REPORTER_USERNAME,
    'password': DHIS2_REPORTER_PASSWORD,
    'content-type': 'json'
}

DHIS2_HEALTH_INDICATORS_NAME_ERASE_SUFFIX_REGEXES = ['\- WEP', r'(?!^\()(?=.+)\(.+\)', r'\(', r'\)']
JSON_EXTENSION = '.json'
KNOWN_MATCHES = {

    #Malaria Cases Treated Matches
    u'(4 Months to 3 Years)'   : u'4+ months to 2 years',
    u'(3+ to 7 Years)'         : u'3+ to 6 years',
    u'(7+ to 12 Years)'        : u'7+ to 11 years',

    # Act Consumption Matches
    u'(Yellow Used)'           : u'6 tablet pack dispensed',
    u'(Yellow in Stock?)'      : u'6 pack balance on hand',
    u'(Blue Used)'             : u'12 tabled pack dispensed',
    u'(Blue in Stock?)'        : u'12 pack on hand',
    u'(Brown Used)'            : u'18 tabled pack dispensed',
    u'(Brown in Stock?)'       : u'18 pack on hand',
    u'(Green Used)'            : u'24 tablet pack dispensed',
    u'(Green in Stock?)'       : u'24 pack on hand',
    u'(Other ACT Used)'        : u'Other ACT dispensed',
    u'(Other ACT in Stock)'    : u'Other balance on hand',
    u'(Quinine Used)'          : u'Quinine dispensed',
    u'(Quinine in Stock?)'     : u'Quinine on hand',
}

MATCHES_REQUIRING_SLUG={
# Malaria cases(disease) -- we need cases_ma and not doc_ma -- who both have the same name
u'Malaria Cases - WEP'     : u'cases_ma'
}

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
        
        if dhis2_indicator_name in MATCHES_REQUIRING_SLUG:
          return Attribute.objects.get(slug=MATCHES_REQUIRING_SLUG[dhis2_indicator_name])
      
        min_match_level = self.match_threshold
        all_mtrack_indicators = Attribute.objects.all()
        matching_indicator = None
        
        if dhis2_indicator_name in KNOWN_MATCHES : 
            dhis2_indicator_name = KNOWN_MATCHES[dhis2_indicator_name]

        for mtrack_indicator in all_mtrack_indicators :
            match_level = self.get_indicators_names_match_level(dhis2_indicator_name, mtrack_indicator.name)
            if match_level >= min_match_level :
                matching_indicator = mtrack_indicator
                min_match_level = match_level

        if matching_indicator :
            return   matching_indicator

    def find_matches_and_update_mapping_table(self, dhis2_dataelement):
        mtrack_indicator  = self.find_matching_indicator_from_mtrack(dhis2_dataelement['name'])
        self.update_dhis2_mapping_db(dhis2_dataelement, mtrack_indicator )

    def update_dhis2_mapping_db (self, dhis2_indicator, mtrack_indicator):
        
        Dhis2_Mtrac_Indicators_Mapping.objects.create(
            eav_attribute = mtrack_indicator,
            dhis2_uuid = dhis2_indicator['id'],
            dhis2_combo_id = dhis2_indicator['combo_id'])


    def get_indicator_combo_option_id(self, url):
        json  =  self.fetch(JSON_EXTENSION, url)
        if (len(json['categoryOptionCombos'])> 1):
            return None
        return json['categoryOptionCombos'][0]['id']

    def get_category_combos_from_combo_category_option(self,url):
        indicators = []
        json  =  self.fetch(JSON_EXTENSION, url)

        for indicator in json['categoryOptionCombos'] :
            indicator['combo_id'] = indicator['id']
            indicators.append(indicator)
        return indicators

    def get_combo_id_from_indicator(self,url):
        json  =  self.fetch(JSON_EXTENSION, url)
        return  self.get_indicator_combo_option_id(json['categoryCombo']['href'])

    def update_mappings_table(self,url):
        json  =  self.fetch(JSON_EXTENSION, url)
        combo_cat_url  = json['categoryCombo']['href']
        comboid =  self.get_indicator_combo_option_id(combo_cat_url)
        if comboid :
            json['combo_id'] = comboid
            self.find_matches_and_update_mapping_table(json)
        else:
            non_default_indicators = self.get_category_combos_from_combo_category_option(combo_cat_url)
            for indicator in non_default_indicators:
                indicator['id'] = json['id']
                self.find_matches_and_update_mapping_table(indicator)

    def fetch_elements_for_dataset(self,url):
      return self.fetch(JSON_EXTENSION, url)['dataElements']

    def fetch_and_update_all(self,url):
        elements = self.fetch_elements_for_dataset(url)
        for element in elements:
            self.update_mappings_table(element['href'])
