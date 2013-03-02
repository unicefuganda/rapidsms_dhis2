#!/usr/bin/env python
from django.template import Context, Template
from django.template.loader import get_template
import urllib2, base64
from mtrack.models import XFormSubmissionExtras
from rapidsms_xforms.models import XFormSubmissionValue, XForm, XFormSubmission
from dhis2.models import Dhis2_Mtrac_Indicators_Mapping , Dhis2_Reports_Report_Task_Log ,Dhis2_Reports_Submissions_Log
from datetime import timedelta
import datetime
from healthmodels.models.HealthFacility import HealthFacilityBase
from xml.dom.minidom import parseString

HMIS033B_REPORT_XML_TEMPLATE = "h033b_reporter.xml"
HMIS_033B_PERIOD_ID = u'%dW%d'
ERROR_MESSAGE_NO_SUBMISSION_EXTRA = 'No XFormSubmissionExtras data exists for the submission '
ERROR_MESSAGE_NO_HMS_INDICATOR    = 'No valid HMS033b indicators reported for the submission'
ERROR_MESSAGE_ALL_VALUES_IGNORED  = 'All values rejected by remote server'
ERROR_MESSAGE_SOME_VALUES_IGNORED = 'Some values rejected by remote server'
ERROR_MESSAGE_CONNECTION_FAILED   = 'Error communicating with the remote server'

class H033B_Reporter(object):
  URL     = "http://ec2-54-242-108-118.compute-1.amazonaws.com/api/dataValueSets"
  HEADERS = {
      'Content-type': 'application/xml',
      'Authorization': 'Basic ' + base64.b64encode("api:P@ssw0rd")
  }

  def send(self, data):
    request = urllib2.Request(self.URL, data = data, headers = self.HEADERS)
    request.get_method = lambda: "POST"
    return urllib2.urlopen(request)

  def submit(self, data):
    xml_request = self.generate_xml_report(data)
    response = self.send(xml_request)
    return self.parse_submission_response(response.read(),xml_request)

  def generate_xml_report(self,data):
    template = get_template(HMIS033B_REPORT_XML_TEMPLATE)
    data = template.render(Context(data))
    return data

  def get_reports_data_for_submission(self,submission_extras_list):
    if submission_extras_list : 
      submission_extras = submission_extras_list[0]
      data = {}
      data['orgUnit']         = submission_extras.facility.uuid
      data['completeDate']    = self.get_utc_time_iso8601(submission_extras.cdate)
      data['period']          = self.get_period_id_for_submission(submission_extras.cdate)
      return data
      
    return None
  
  def set_data_values_from_submission_value(self,data,submission_values):
    data['dataValues']    = []
    for submission_value in submission_values : 
      dataValue = self.get_data_values_for_submission(submission_value)
      if dataValue :
        data['dataValues'].append(dataValue)

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
    self.current_task =  Dhis2_Reports_Report_Task_Log.objects.create()
    
  def log_submission_finished(self,submission_count, status, description='') :
    log_record = self.current_task
    log_record.time_finished= datetime.datetime.now()
    log_record.number_of_submissions = submission_count
    log_record.status = status
    log_record.description = description
    log_record.save()
    
  def parse_submission_response(self,response_xml,request_xml):
    
    dom = parseString(response_xml)
    result=dom.getElementsByTagName('dataValueCount')[0]
    imported  =int(result.getAttribute('imported'))
    updated   =int(result.getAttribute('updated'))
    ignored   =int(result.getAttribute('ignored'))
    error=None
    
    conflicts = dom.getElementsByTagName('conflict')
    if conflicts : 
      error = ''
      for conflict in conflicts : 
        error+='%s  : %s\n'%(conflict.getAttribute('object') ,conflict.getAttribute('value'))
        
    result= {}
    result['imported']  = imported
    result['updated']   = updated
    result['ignored']   = ignored
    result['error']     = error
    result['request_xml']=request_xml
    
    return result
    
  
  def get_data_submission(self,submission):                                                                       
    data = None
    failure_description = None
    try : 
      a=XFormSubmissionExtras.objects.filter(submission=submission)
      data  =  self.get_reports_data_for_submission(a)      
    
      if not data :
        raise LookupError(ERROR_MESSAGE_NO_SUBMISSION_EXTRA)
    
      submission_values = XFormSubmissionValue.objects.filter(submission=submission)  
      self.set_data_values_from_submission_value(data,submission_values)
    
      if not data['dataValues'] : 
        raise LookupError(ERROR_MESSAGE_NO_HMS_INDICATOR)
      
    except LookupError, e:
      failure_description = str(e)
    except Exception, e:
      exception = type(e).__name__ +":"+ str(e)
      failure_description = 'Unknown Erorr ! : %s'%(exception) 
  
    if failure_description : 
      report_submissions_log = Dhis2_Reports_Submissions_Log.objects.create(
          task_id       = self.current_task,
          submission_id = submission.id, 
          result        = Dhis2_Reports_Submissions_Log.INVALID_SUBMISSION_DATA,
          description   = failure_description 
          )

    return data
  
  def submit_submission(self,submission):
    data =self.get_data_submission(submission)
    result = self.submit(data)
    accepted_attributes_values = result['updated'] + result['imported']
    log_message=''
    sucess = False
    
    if result['error'] :      
      log_result  = Dhis2_Reports_Submissions_Log.ERROR
      log_message = result['error']
    elif not accepted_attributes_values : 
      log_message = ERROR_MESSAGE_ALL_VALUES_IGNORED
      log_result  = Dhis2_Reports_Submissions_Log.ERROR
    elif result['ignored'] : 
      log_message = ERROR_MESSAGE_SOME_VALUES_IGNORED
      log_result  = Dhis2_Reports_Submissions_Log.SOME_ATTRIBUTES_IGNORED
    else :
      log_result  = Dhis2_Reports_Report_Task_Log.SUCCESS
      sucess =True
    
    Dhis2_Reports_Submissions_Log.objects.create(
        task_id = self.current_task,
        submission_id = submission.id,
        reported_xml = result['request_xml'], 
        result = log_result,
        description =log_message
        )
  def initiate_weekly_reports_submission(self,date):
    last_monday = self.get_last_sunday(date) + timedelta(days=1)
    submissions_for_last_week = self.get_submissions_in_date_range(last_monday, date)
    self.log_submission_started()
    sucesssful_submissions  =  0
    connection_failed = False
    status = Dhis2_Reports_Report_Task_Log.SUCCESS
    description = ''
    
    for submission in submissions_for_last_week:
      try :
        if self.submit_submission(submission) :
          sucesssful_submissions +=1          
      except urllib2.URLError , e: 
        exception = type(e).__name__ +":"+ str(e)
        connection_failed = True
        status = Dhis2_Reports_Report_Task_Log.FAILED
        description = ERROR_MESSAGE_CONNECTION_FAILED + ' Exception : '+exception
        break
    
    
    self.log_submission_finished(
      submission_count=successful_submissions,
      status= status,
      description=description)
  