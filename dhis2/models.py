from django.db import models
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
    mtrac_id =  models.ForeignKey(Attribute)
    dhis2_uuid = models.CharField(max_length=50)
    dhis2_name  = models.CharField(max_length=255)
    dhis2_url  = models.CharField(max_length=255)
    dhis2_combo_id = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.dhis2_name
    
    class Meta:
        db_table = u'dhis2_mtrack_indicators_mapping'
    



