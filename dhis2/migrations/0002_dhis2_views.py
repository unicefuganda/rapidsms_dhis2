# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

def run_file(file_name):
    import os
    f = open(os.path.join(os.path.dirname(__file__),file_name))
    query = f.read()
    db.execute(query)

class Migration(SchemaMigration):
    def forwards(self, orm):
        db.execute("DROP VIEW IF EXISTS submissions_values_view;")
        db.execute("DROP VIEW IF EXISTS xform_submissions_view2;")
        #create the two views
        run_file('0002_dhis2_views.sql')
    def backwards(self, orm):
        db.execute("DROP VIEW submissions_values_view CASCADE;")
        db.execute("DROP VIEW xform_submissions_view2 CASCADE;")

    models = {
        'dhis2.codestatus': {
            'Meta': {'object_name': 'CodeStatus', 'db_table': "u'code_status'"},
            'cdate': ('django.db.models.fields.DateTimeField', [], {}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'created': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dups': ('django.db.models.fields.TextField', [], {}),
            'facility': ('django.db.models.fields.TextField', [], {}),
            'fid': ('django.db.models.fields.IntegerField', [], {}),
            'ftype': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'fuzzy_matched': ('django.db.models.fields.TextField', [], {}),
            'has_dups': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'pmatch': ('django.db.models.fields.DecimalField', [], {'max_digits': '65535', 'decimal_places': '3'})
        },
        'dhis2.dhis2mapping': {
            'Meta': {'object_name': 'Dhis2Mapping', 'db_table': "u'dhis2_mapping'"},
            'cdate': ('django.db.models.fields.DateTimeField', [], {}),
            'dhis2_dataelement': ('django.db.models.fields.TextField', [], {}),
            'dhis2_type': ('django.db.models.fields.TextField', [], {}),
            'dhis2_uid': ('django.db.models.fields.TextField', [], {}),
            'field_slug': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['dhis2']
