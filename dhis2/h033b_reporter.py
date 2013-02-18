#!/usr/bin/env python
from django.template import Context, Template
from django.template.loader import get_template
import urllib2, base64
from mtrack.models import XFormSubmissionExtras
from rapidsms_xforms.models import XFormSubmissionValue, XForm, XFormSubmission



class H033B_Reporter(object):
  URL     = "http://dhis/api/dataValueSets"
  HEADERS = {
      'Content-type': 'application/xml',
      'Authorization': 'Basic ' + base64.b64encode("api:P@ssw0rd")
  }

  @classmethod
  def send(self, data):
    request = urllib2.Request(self.URL, data = data, headers = self.HEADERS)
    request.get_method = lambda: "POST"
    return urllib2.urlopen(request)

  @classmethod
  def submit(self, data):
    template = get_template("h033b_reporter.xml")
    data = template.render(Context(data))
    return self.send(data)
  
  
  @classmethod
  def get_reports_data_for_submission(self,submission_arg):
    submission_extras = XFormSubmissionExtras.objects.filter(submission=submission_arg)[0]
    data = {}
    data['orgUnit']         = submission_extras.facility_id
    data['completeDate']    = submission_arg.created 
    data['dataValues']      = {}
    
    submission_values = XFormSubmissionValue.objects.filter(submission=submission_arg)
    for submission_value in submission_values : 
      data['dataValues'][ submission_value.attribute_id ] = submission_value.value

    return data
  
  @classmethod
  def get_submissions_in_date_range(self,from_date,to_date):
    return XFormSubmission.objects.filter(created__range=[from_date, to_date])
    
  @classmethod
  def get_utc_time_iso8601(self,time_arg):
    year_str = str(time_arg.year)
    month_str =str(time_arg.month)
    day_str = str(time_arg.day)
    hour_str = str(time_arg.hour)
    minute_str = str(time_arg.minute)
    second_str = str(time_arg.second)

    if len(month_str) <2 : 
      month_str = str(0)+ month_str
    if len(day_str) <2 : 
      day_str = str(0)+ day_str
    if len(hour_str) <2 : 
      hour_str = str(0)+ hour_str
    if len(minute_str) <2 : 
      minute_str = str(0)+ minute_str
    if len(second_str) <2 : 
      second_str = str(0)+ second_str

    return '%s-%s-%sT%s:%s:%sZ'%(year_str,month_str,day_str,hour_str,minute_str,second_str)

  @classmethod
  def get_dhis2_orgunit_uuid(self,health_facility_base_id):
    ######################
    # TODO  
    ######################
    return '6VeE8JrylXn'

  @classmethod
  def prepare_report_for_submission_to_dhis(self,data):
    expected  = { 
      'orgUnit': "6VeE8JrylXn",
      'completeDate': "2012-11-11T00:00:00Z",
      'period': '201211',
      'dataValues': [
                      {
                        'dataElement': 'mdIPCPfqXaJ',
                        'value': 99,
                        'categoryOptionCombo' :'gGhClrV5odI'
                      },      
                      {
                        'dataElement': 'U7cokRIptxu',
                        'value': 100,
                        'categoryOptionCombo' : 'gGhClrV5odI'
                      }
                    ]
              }
    return expected
  