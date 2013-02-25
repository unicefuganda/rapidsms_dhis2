#!/usr/bin/env python
from django.template import Context, Template
from django.template.loader import get_template
import urllib2, base64
from mtrack.models import XFormSubmissionExtras
from rapidsms_xforms.models import XFormSubmissionValue, XForm, XFormSubmission
from dhis2.models import Dhis2_Mtrac_Indicators_Mapping , Dhis2_Reports_Report_Task_Log
from datetime import timedelta
import datetime
from healthmodels.models.HealthFacility import HealthFacilityBase

HMIS033B_REPORT_XML_TEMPLATE = "h033b_reporter.xml"
HMIS_033B_PERIOD_ID = u'%dW%d'

class H033B_Reporter(object):
  URL     = "http://dhis/api/dataValueSets"
  HEADERS = {
      'Content-type': 'application/xml',
      'Authorization': 'Basic ' + base64.b64encode("api:P@ssw0rd")
  }

  def send(self, data):
    request = urllib2.Request(self.URL, data = data, headers = self.HEADERS)
    request.get_method = lambda: "POST"
    return urllib2.urlopen(request)

  def submit(self, data):
    return self.send(self.generate_xml_report(data))
  
  def generate_xml_report(self,data):
    template = get_template(HMIS033B_REPORT_XML_TEMPLATE)
    data = template.render(Context(data))
    return data
    
  def get_reports_data_for_submission(self,submission_arg):
    submission_extras_list = XFormSubmissionExtras.objects.filter(submission=submission_arg)
    if submission_extras_list : 
      submission_extras = submission_extras_list[0]
      data = {}
      data['orgUnit']         = submission_extras.facility.uuid
      data['completeDate']    = self.get_utc_time_iso8601(submission_arg.created)
      data['period']          = self.get_period_id_for_submission(submission_arg.created)
      data['dataValues']      = []

      submission_values = XFormSubmissionValue.objects.filter(submission=submission_arg)
      for submission_value in submission_values : 
        dataValue = self.get_data_values_for_submission(submission_value)
        if dataValue :
          data['dataValues'].append(dataValue)
      return data
    return None
    
  def get_data_values_for_submission(self, submission_value):
    data_value = {}
    attrib_id = submission_value.attribute_id
    dhis2_mapping = Dhis2_Mtrac_Indicators_Mapping.objects.filter(mtrac_id=attrib_id)

    if dhis2_mapping:
      element_id = dhis2_mapping[0].dhis2_uuid
      combo_id = dhis2_mapping[0].dhis2_combo_id
      data_value['dataElement'] = element_id
      data_value['value'] = submission_value.value
      data_value['categoryOptionCombo']  =combo_id
    return data_value
    
  def get_submissions_in_date_range(self,from_date,to_date):
    return XFormSubmission.objects.filter(created__range=[from_date, to_date])
    
  def process_and_send_reports_for_last_week(self, date):
    last_monday = self.get_last_sunday(date) + timedelta(days=1)
    submissions_for_last_week = self.get_submissions_in_date_range(last_monday, date)
    log_id = self.log_submission_started()
    success_submissions_made=0
    failure_submissions_made=0
    failure_descriptions = []
    
    for submission in submissions_for_last_week:
      data = self.get_reports_data_for_submission(submission) 
      if data : 
        try:
          self.submit(data)
          success_submissions_made += 1
        except   Exception, e:
          exception = type(e).__name__ +":"+ str(e)
          failure_description = 'Failed to submit submission_id#%s. \nException: %s '%(submission.id,exception) 
          failure_descriptions.append(failure_description)
          failure_submissions_made += 1

    if success_submission_made >0:      
      self.log_submission( log_id=log_id, submission_count=success_submission_made, status=Dhis2_Reports_Report_Task_Log.SUCCESS) 
    if failure_submission_made >0:  
      failiure_description = "failed to submit %d reports."%failure_submissions_made + failure_descriptions
      self.log_submission( log_id=log_id, submission_count=success_submission_made, status=Dhis2_Reports_Report_Task_Log.FAILURE, description = failiure_description) 

  @classmethod  
  def get_week_period_id_for_sunday(self, date):
    year  = date.year
    weekday =  int(date.strftime("%W")) + 1
    return HMIS_033B_PERIOD_ID%(year,weekday) 
    
  @classmethod
  def get_last_sunday(self, date):
    offset_from_last_sunday = date.weekday()+1 
    last_sunday = date  - timedelta(days= offset_from_last_sunday)
    return last_sunday  
    
  @classmethod
  def get_period_id_for_submission(self,date):
    return self.get_week_period_id_for_sunday(self.get_last_sunday(date))   
    
  @classmethod
  def get_utc_time_iso8601(self,time_arg):
    year_str   = str(time_arg.year)
    month_str  = str(time_arg.month)
    day_str    = str(time_arg.day)
    hour_str   = str(time_arg.hour)
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
    

  def log_submission_started(self) : 
    return Dhis2_Reports_Report_Task_Log.objects.create().id
    
  def log_submission_finished_with_success(self, log_id, submission_count, status, description='') :
    log_record = Dhis2_Reports_Report_Task_Log.objects.get(id=log_id)
    log_record.time_finished= datetime.datetime.now()
    log_record.number_of_submissions = submission_count
    log_record.status = status
    log_record.description = description
    log_record.save()
    


    