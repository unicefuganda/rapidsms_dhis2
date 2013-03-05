from django.contrib import admin
from .models import CodeStatus, Dhis2Mapping
from dhis2.models import Dhis2_Mtrac_Indicators_Mapping

class Indicators_Mapping_Admin(admin.ModelAdmin):
    fields = ['mtrac_id', 'dhis2_uuid']
    
    
admin.site.register(Dhis2_Mtrac_Indicators_Mapping, Indicators_Mapping_Admin)
 