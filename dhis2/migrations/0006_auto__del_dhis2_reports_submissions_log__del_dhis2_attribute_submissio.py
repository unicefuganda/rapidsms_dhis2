# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Dhis2_Reports_Submissions_Log'
        db.delete_table(u'dhis2_reports_submissions_log')

        # Deleting model 'Dhis2_Attribute_Submission_Log'
        db.delete_table(u'dhis2_attribute_submissions_log')

        # Adding model 'Dhis2_Reports_Report_Task_Log'
        db.create_table(u'dhis2_reports_submissions_log', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time_started', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('time_finished', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('number_of_submissions', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='RUNNING', max_length=15)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('dhis2', ['Dhis2_Reports_Report_Task_Log'])


    def backwards(self, orm):
        # Adding model 'Dhis2_Reports_Submissions_Log'
        db.create_table(u'dhis2_reports_submissions_log', (
            ('status', self.gf('django.db.models.fields.CharField')(default='RUNNING', max_length=15)),
            ('time_finished', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True)),
            ('number_of_submissions', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time_started', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('dhis2', ['Dhis2_Reports_Submissions_Log'])

        # Adding model 'Dhis2_Attribute_Submission_Log'
        db.create_table(u'dhis2_attribute_submissions_log', (
            ('submission_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rapidsms_xforms.XFormSubmission'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True)),
            ('report_log_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dhis2.Dhis2_Reports_Submissions_Log'])),
            ('attribute_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eav.Attribute'])),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('dhis2', ['Dhis2_Attribute_Submission_Log'])

        # Deleting model 'Dhis2_Reports_Report_Task_Log'
        db.delete_table(u'dhis2_reports_submissions_log')


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
        'dhis2.dhis2_reports_report_task_log': {
            'Meta': {'object_name': 'Dhis2_Reports_Report_Task_Log', 'db_table': "u'dhis2_reports_submissions_log'"},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number_of_submissions': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'RUNNING'", 'max_length': '15'}),
            'time_finished': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'time_started': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'dhis2.dhis2_temp_mtrac_indicators_mapping': {
            'Meta': {'object_name': 'Dhis2_Temp_Mtrac_Indicators_Mapping', 'db_table': "u'dhis2_temp_mtrack_indicators_mapping'"},
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