# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Dhis2_Mtrac_Indicators_Mapping'
        db.create_table(u'dhis2_mtrack_indicators_mapping', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mtrac_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('dhis2_uuid', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('dhis2_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('dhis2_url', self.gf('django.db.models.fields.CharField')(max_length=260)),
            ('dhis2_combo_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('dhis2', ['Dhis2_Mtrac_Indicators_Mapping'])


    def backwards(self, orm):
        # Deleting model 'Dhis2_Mtrac_Indicators_Mapping'
        db.delete_table(u'dhis2_mtrack_indicators_mapping')


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
            'pmatch': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '3'})
        },
        'dhis2.dhis2_mtrac_indicators_mapping': {
            'Meta': {'object_name': 'Dhis2_Mtrac_Indicators_Mapping', 'db_table': "u'dhis2_mtrack_indicators_mapping'"},
            'dhis2_combo_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'dhis2_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'dhis2_url': ('django.db.models.fields.CharField', [], {'max_length': '260'}),
            'dhis2_uuid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mtrac_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
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