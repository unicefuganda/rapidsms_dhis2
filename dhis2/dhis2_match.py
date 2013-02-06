import urllib2
import base64
import json
import re
import psycopg2
import psycopg2.extras
import Levenshtein
from eav.models import Attribute

MTRACK_CONFIG = {
  'dbhost': 'localhost',
  'dbname': 'mtrack',
  'dbuser': 'mnandri',
  'dbpass': '',
}

HEALTH_INDICATORS_NAME_ERASE_SUFFIX = ['- WEP']

pg_connection = psycopg2.connect("dbname=" + MTRACK_CONFIG['dbname'] + " host= "+MTRACK_CONFIG['dbhost'] + " user=" + MTRACK_CONFIG['dbuser'] + " password=" + MTRACK_CONFIG['dbpass'])
pg_cursor = pg_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

DHIS2_CONFIG = {
  'urls': {
            'diseases': 'http://dhis/api/dataSets',
          },
  'user': 'sekiskylink',
  'password': '123Congse',
  'content-type': 'json'
}

class Dhis2_Fetch_Health_Indicators(object):
  def __init__(self, match_threshold):
    self.match_threshold = match_threshold
    auth = base64.b64encode("%(user)s:%(password)s" % DHIS2_CONFIG)
    self.HEADERS = {
                      'Content-type': 'application/json; charset="UTF-8"',
                      'Authorization': 'Basic '+auth
                    }
				
    self.BASE_URL = DHIS2_CONFIG['urls']			

  def get_dataset(self, extension, url = None, query = None):
	url = (url or self.BASE_URL['diseases']) + extension
	if query:
		url += "?" + query

	request = urllib2.Request(url, headers=self.HEADERS)
	response = urllib2.urlopen(request)
	return json.loads(response.read())

  def compare_strings(self, some_string, another_string):
    ratio = Levenshtein.ratio(some_string.strip().lower(), another_string.strip().lower())
    return round(ratio * 100)

  def get_indicators_names_match_level(self, dhis2_name, mtrack_name):
    dhis2_name = dhis2_name.strip()
    for x in HEALTH_INDICATORS_NAME_ERASE_SUFFIX : 
        dhis2_name = dhis2_name.replace(x,'')
    dhis2_name = dhis2_name.strip()

    return self.compare_strings(dhis2_name, mtrack_name) 
    
  def find_matching_indicator_from_mtrack(self,dhis2_indicator_name):
      min_match_level = self.match_threshold 
      all_mtrack_indicators = Attribute.objects.all()
      matching_indicator = None
      
      for mtrack_indicator in all_mtrack_indicators : 
        match_level = self.get_indicators_names_match_level(dhis2_indicator_name, mtrack_indicator.name)
        if match_level >= min_match_level : 
          matching_indicator = mtrack_indicator
          min_match_level = match_level
      
      if matching_indicator : 
        return   matching_indicator.id , matching_indicator.name,matching_indicator.slug
      
      
    

  

  