from django.db import models
from rapidsms_xforms.models import XFormSubmission
from eav.models import Attribute

class Dhis2_Mtrac_Indicators_Mapping(models.Model):
  eav_attribute    = models.ForeignKey(Attribute,  unique=True)
  dhis2_uuid  = models.CharField(max_length=50)
  dhis2_combo_id =models.CharField(max_length=50)
  
  def __unicode__(self):
      return self.eav_attribute.name
      
  class Meta:
    db_table = u'dhis2_mtrack_indicators_mapping'
    verbose_name = u'Dhis2 Mtrac Indicator Mapping'
    
class Dhis2_Temp_Mtrac_Indicators_Mapping(models.Model):
  mtrac_id    = models.IntegerField(null=True)
  dhis2_uuid  = models.CharField(max_length=50)
  dhis2_name  = models.CharField(max_length=100)
  dhis2_url   = models.CharField(max_length=260)
  dhis2_combo_id =models.CharField(max_length=50)

  def __unicode__(self):
      return u'tmp: ' + self.dhis2_name

  class Meta:
    db_table = u'dhis2_temp_mtrack_indicators_mapping'    

class Dhis2_Reports_Report_Task_Log(models.Model):
  RUNNING = 'RUNNING'
  FAILED  = 'FAILED'
  SUCCESS = 'SUCCESS'
  time_started          = models.DateTimeField(auto_now_add=True, blank=True)
  time_finished         = models.DateTimeField(null=True)
  number_of_submissions = models.IntegerField(null=True)
  status                = models.CharField(max_length=15, default=RUNNING)
  description           = models.TextField(null=True)

  class Meta:
    db_table = u'dhis2_reports_submissions_log'


class Dhis2_Reports_Submissions_Log(models.Model):
  SUCCESS = "SUCCESS"
  INVALID_SUBMISSION_DATA  = "INVALID_SUBMISSION_DATA"
  NON_REPORTING_FACILITIES  = "NON_REPORTING_FACILITIES"
  SOME_ATTRIBUTES_IGNORED = "SOME_ATTRIBUTES_IGNORED"
  ERROR                   = 'ERROR'
  FAILED                  = 'FAILED'
  task_id               = models.ForeignKey(Dhis2_Reports_Report_Task_Log)
  submission_id         = models.IntegerField()
  reported_xml          = models.TextField(null=True)
  result                = models.CharField(max_length=50)
  description           = models.TextField(null=True)

  class Meta:
    db_table = u'dhis2_attribute_submissions_log'
