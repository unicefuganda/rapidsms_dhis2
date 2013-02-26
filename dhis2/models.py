from django.db import models
from rapidsms_xforms.models import XFormSubmission
from eav.models import Attribute
def promote(modeladmin, request, queryset):
    queryset.update(created=True)

promote.short_description = "Update facility Code"
# Create your models here.
class CodeStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    facility = models.TextField()
    ftype = models.CharField(max_length=32)
    code = models.CharField(max_length=32)
    created = models.BooleanField()
    has_dups = models.BooleanField()
    fuzzy_matched = models.TextField()
    dups = models.TextField()
    pmatch = models.DecimalField(max_digits=5, decimal_places=3)
    fid = models.IntegerField()
    cdate = models.DateTimeField()
    class Meta:
        db_table = u'code_status'

    def __unicode__(self):
        if self.created:
            r = "(*)"
        else: r = ""
        return "%s %s ===> %s %s ===>%s"%(self.facility, self.ftype, self.fuzzy_matched, self.ftype, r)

class Dhis2Mapping(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    field_slug = models.TextField()
    keyword = models.TextField()
    dhis2_uid = models.TextField()
    dhis2_type = models.TextField()
    dhis2_dataelement = models.TextField()
    cdate = models.DateTimeField()

    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'dhis2_mapping'

class Dhis2_Mtrac_Indicators_Mapping(models.Model):
  mtrac_id    = models.IntegerField(null=True)
  dhis2_uuid  = models.CharField(max_length=50)
  dhis2_name  = models.CharField(max_length=100)
  dhis2_url   = models.CharField(max_length=260)
  dhis2_combo_id =models.CharField(max_length=50)
  
  def __unicode__(self):
      return self.dhis2_name
      
  class Meta:
    db_table = u'dhis2_mtrack_indicators_mapping'
    
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
  SOME_ATTRIBUTES_IGNORED = "SOME_ATTRIBUTES_IGNORED"
  ERROR                   = 'ERROR'
  task_id               = models.ForeignKey(Dhis2_Reports_Report_Task_Log)
  submission_id         = models.IntegerField()
  reported_xml          = models.TextField(null=True)
  result                = models.CharField(max_length=50)
  description           = models.TextField(null=True)

  class Meta:
    db_table = u'dhis2_attribute_submissions_log'