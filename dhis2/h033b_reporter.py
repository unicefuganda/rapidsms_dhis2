#!/usr/bin/env python
from django.template import Context, Template
from django.template.loader import get_template
import urllib2, base64
from mtrack.models import XFormSubmissionExtras
from rapidsms_xforms.models import XFormSubmissionValue, XForm, XFormSubmission
from dhis2.models import Dhis2_Mtrac_Indicators_Mapping



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
    data['orgUnit']         = submission_extras.facility.uuid
    data['completeDate']    = submission_arg.created 
    data['dataValues']      = []
    
    submission_values = XFormSubmissionValue.objects.filter(submission=submission_arg)
    for submission_value in submission_values : 
      data_value = {}
      attrib_id = submission_value.attribute_id
      dhis2_mapping = Dhis2_Mtrac_Indicators_Mapping.objects.filter(mtrac_id=attrib_id)
      if dhis2_mapping:
        element_id = dhis2_mapping[0].dhis2_uuid
        combo_id = dhis2_mapping[0].dhis2_combo_id
      
        data_value['dataElement'] = element_id
        data_value['value'] = submission_value.value
        data_value['categoryOptionCombo']  =combo_id
        data['dataValues'] .append(data_value)
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
  def prepare_report_for_submission_to_dhis(self,data):
    attribute_values_list = data['dataValues'] 
    dataElement_values= []
    for attribute_values in attribute_values_list :
      for attribute in  attribute_values: 
        dataElement_value = {}
        dhis2_mapping = Dhis2_Mtrac_Indicators_Mapping.objects.filter(mtrac_id=attribute)[0]
        dataElement_value['dataElement'] = dhis2_mapping.dhis2_uuid
        dataElement_value['value']= attribute_values[attribute]
        dataElement_value['categoryOptionCombo'] = dhis2_mapping.dhis2_combo_id
        dataElement_values.append(dataElement_value)
      
    data['dataValues'] = dataElement_values
    
    return data
    
  @classmethod
  def get_dataelement_id_and_combo_id_for_attribute(self,attribute_id):
    dhis2_mapping = Dhis2_Mtrac_Indicators_Mapping.objects.filter(mtrac_id=attribute_id)[0]
    return dhis2_mapping.dhis2_uuid,dhis2_mapping.dhis2_combo_id
    