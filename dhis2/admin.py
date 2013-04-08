from django.contrib import admin
from dhis2.models import Dhis2_Mtrac_Indicators_Mapping

class Indicators_Mapping_Admin(admin.ModelAdmin):
    fields = ['eav_attribute', 'dhis2_uuid','dhis2_combo_id']
    
    
admin.site.register(Dhis2_Mtrac_Indicators_Mapping, Indicators_Mapping_Admin)
 