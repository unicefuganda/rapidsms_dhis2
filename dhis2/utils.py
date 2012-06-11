from django.conf import settings
from django.db import connections, transaction
import sys
import os
import base64
import json
import random
import pprint
import psycopg2
import psycopg2.extras
import difflib
import re
import datetime

try:
    import httplib2
    Http = httplib2.Http
except ImportError:
    import urllib2
    class Http(): # wrapper to use when httplib2 not available
        def request(self, url, method, body, headers):
            f = urllib2.urlopen(urllib2.Request(url, body, headers))
            return f.info(), f.read()

config = getattr(settings, 'DHIS2_CONFIG', {
            'dhis2_url': 'http://localhost:8080/dhis/api/',
            'dhis2_user': 'sekiskylink',
            'dhis2_passwd': '123Congse',
            'ctype': 'json', # when reading, json will be easier for python
            'FIRSTDAY_OF_RWEEK':4
        })


db_config = connections['default'].settings_dict
dbhost = db_config['HOST']
dbname = db_config['NAME']
dbuser = db_config['USER']
dbpasswd = db_config['PASSWORD']

conn = psycopg2.connect("dbname=" + dbname + " host= " + dbhost + " user=" + dbuser + " password=" + dbpasswd)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

http = Http()

FIELD_MAP = {}

def lit(**keywords):
        return keywords

def flatten(l):
    return [item for sublist in l for item in sublist]

def find_closest_match(s, choice_list):
    r = difflib.get_close_matches(s, choice_list)
    return r[0] if r else []

def last_reporting_period(xdate=datetime.datetime.now(), period=1, weekday=getattr(config, 'FIRSTDAY_OF_RWEEK', 4), todate=False):
    """
    Find a date range that spans from the most recent Wednesday (exactly a week ago if
    today is Wednesday) to the beginning of Thursday, one week prior

    if period is specified, this wednesday can be exactly <period> weeks prior
    """
    d = xdate
    d = datetime.datetime(d.year, d.month, d.day)
    # find the past day with weekday() of 3
    last_thursday = d - datetime.timedelta((((7 - weekday) + d.weekday()) % 7)) - datetime.timedelta((period - 1) * 7)
    return (last_thursday - datetime.timedelta(7), datetime.datetime.now() if todate else last_thursday,)

def last_reporting_period_number(day):
    first_monday = last_reporting_period(xdate=day, weekday=getattr(config, 'FIRSTDAY_OF_RWEEK', 4), period=1)[0]
    start_of_year = datetime.datetime(first_monday.year, 1, 1, 0, 0, 0)
    td = first_monday - start_of_year
    toret = int(td.days / 7)
    if start_of_year.weekday() != 0:
        toret += 1
    return toret

def current_reporting_week_number(day):
    #if Monday is first day of Week
    #return int(time.strftime('%W'))
    return last_reporting_period_number(day) + 1

def current_week_reporting_range(day):
    return last_reporting_period(xdate=day, period=0)

def get_reporting_week_for_day(day=datetime.datetime.now()):
    return last_reporting_period_number(day) + 1

def read_url(url, paging=True):
    if not paging:
        c = '&' if url.find('?') else '?'
        url += c + 'paging=false'
    HTTP_METHOD = "GET"
    auth = base64.b64encode("%(dhis2_user)s:%(dhis2_passwd)s" % config)
    headers = {
            'Content-type': 'application/json; charset="UTF-8"',
            'Authorization': 'Basic ' + auth
        }
    response, content = http.request(url, HTTP_METHOD, headers=headers)
    return content

#read data given UID
def read_data(elem_type, uid):
    HTTP_METHOD = "GET"
    url = "%s%s/%s.%s" % (config['dhis2_url'], elem_type, uid, config['ctype'])
    auth = base64.b64encode("%(dhis2_user)s:%(dhis2_passwd)s" % config)
    headers = {
            'Content-type': 'application/json; charset="UTF-8"',
            'Authorization': 'Basic ' + auth
        }
    response, content = http.request(url, HTTP_METHOD, headers=headers)
    return content

def read_data_withoutUID(elem_type):
    HTTP_METHOD = "GET"
    url = "%s%s.%s?paging=false" % (config['dhis2_url'], elem_type, config['ctype'])
    print url
    auth = base64.b64encode("%(dhis2_user)s:%(dhis2_passwd)s" % config)
    headers = {
            'Content-type': 'application/json; charset="UTF-8"',
            'Authorization': 'Basic ' + auth
        }
    response, content = http.request(url, HTTP_METHOD, headers=headers)
    return content

def send_data(requestXml):
    HTTP_METHOD = "POST"
    url = "%sdataValueSets" % (config['dhis2_url'])
    print url
    auth = base64.b64encode("%(dhis2_user)s:%(dhis2_passwd)s" % config)
    headers = {
            'Content-type': 'text/xml; charset="UTF-8"',
            'Authorization': 'Basic ' + auth
        }
    response, content = http.request(url, HTTP_METHOD, body=requestXml, headers=headers)
    return response

def get_facilities_by_type(ftype):
    query = ("WITH facilities AS (SELECT a.id, a.name, a.code, type_id, b.name AS ftype "
                "FROM healthmodels_healthfacilitybase a, healthmodels_healthfacilitytypebase b "
                "WHERE a.type_id = b.id) SELECT id, name FROM facilities WHERE ftype = '%s';"
                )
    query = query % ftype
    cur.execute(query)
    res = cur.fetchall()
    return res
    #return [r['name'] for r in res]

def update_field(dic):
    query = ("UPDATE %(table)s SET %(col)s ='%(val)s' WHERE %(idfield)s = '%(idvalue)s'")
    query = query % dic
    cur.execute(query)
    conn.commit()

def log_code_insert(fields):
    query = ("INSERT INTO code_status(facility, ftype, code, created, has_dups,fuzzy_matched, dups,pmatch,fid)"
                " VALUES (E'%(facility)s','%(ftype)s', '%(code)s', '%(created)s','%(has_dups)s',E'%(fuzzy_matched)s',"
                "'%(dups)s','%(pmatch)s','%(fid)s')")
    query = query % fields
    cur.execute(query)
    conn.commit()

def get_dhis_mtrack_field_mapping():
    global FIELD_MAP
    query = ("SELECT DISTINCT field_slug,name, keyword,dhis2_uid, dhis2_dataelement from dhis2_mapping")
    cur.execute(query)
    res = cur.fetchall()
    for r in res:
        FIELD_MAP['%s' % r['field_slug']] = {'dataElement':r['dhis2_dataelement'], 'categoryOptionCombo':r['dhis2_uid']}


#get report data organised according to facility/orgunits
def get_reports(date_range=current_week_reporting_range(datetime.datetime.now())):
    #remember to order reports by date as dhis2 overrides older  reports with new ones
    query = ("SELECT submissionid, keyword, slug, facility, value, date FROM the_values"
            " WHERE has_errors='f' AND value <> '' AND facility IS NOT NULL AND "
            "facility NOT LIKE 'gen%%' AND date BETWEEN '%s' AND '%s' ORDER BY facility, date ASC")
    #later remove the facility not like 'gen%%'
    query = query % (date_range[0], date_range[1])
    cur.execute(query)
    res = cur.fetchall()
    # I think it is wiser to order this data in facilities/orgunits
    ORGUNIT_DATA_DICT = {}
    for r in res:
        if r['facility'] not in ORGUNIT_DATA_DICT:
            ORGUNIT_DATA_DICT[r['facility']] = [r]
        else:
            ORGUNIT_DATA_DICT[r['facility']].append(r)
    return ORGUNIT_DATA_DICT

def build_uploadXML(orgunit, week, data):
    datavalues = """"""
    for d in data:
        datavalue_dict = FIELD_MAP[d['slug']]
        datavalue_dict.update({'value': d['value']})
        if datavalue_dict['dataElement'] and datavalue_dict['categoryOptionCombo']:
            tmp = """<dataValue dataElement="%(dataElement)s" categoryOptionCombo="%(categoryOptionCombo)s" value="%(value)s"/>"""
            datavalues += tmp % (datavalue_dict)
    #we assume date completed = current date
    _Xml = """<?xml version="1.0"?>
<dataValueSet xmlns="http://dhis2.org/schema/dxf/2.0" period="%s" completeDate="%s" orgUnit="%s">%s</dataValueSet>"""
    postXml = _Xml % (week, datetime.datetime.now().strftime('%F'), orgunit, datavalues)
    return postXml.replace('\n', '')

#make some useful calls
get_dhis_mtrack_field_mapping()

conn.close()
