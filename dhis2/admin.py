from django.contrib import admin
from .models import CodeStatus, Dhis2Mapping

from django.db import models


def promote(modeladmin, request, queryset):
    queryset.update(created=True)

promote.short_description = "Update facility Code"

class Dhis2MappingAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('keyword',)
    #filter_horizontal = ('permissions',)

class CodeStatusAdmin(admin.ModelAdmin):
    ordering = ('pmatch',)
    actions = [promote]

admin.site.register(CodeStatus,CodeStatusAdmin)
admin.site.register(Dhis2Mapping,Dhis2MappingAdmin)

