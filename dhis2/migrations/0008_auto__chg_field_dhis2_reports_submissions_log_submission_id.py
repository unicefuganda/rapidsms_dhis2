# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Renaming column for 'Dhis2_Reports_Submissions_Log.submission_id' to match new field type.
        db.rename_column(u'dhis2_attribute_submissions_log', 'submission_id_id', 'submission_id')
        # Changing field 'Dhis2_Reports_Submissions_Log.submission_id'
        db.alter_column(u'dhis2_attribute_submissions_log', 'submission_id', self.gf('django.db.models.fields.IntegerField')())
        # Removing index on 'Dhis2_Reports_Submissions_Log', fields ['submission_id']
        db.delete_index(u'dhis2_attribute_submissions_log', ['submission_id_id'])


    def backwards(self, orm):
        # Adding index on 'Dhis2_Reports_Submissions_Log', fields ['submission_id']
        db.create_index(u'dhis2_attribute_submissions_log', ['submission_id_id'])


        # Renaming column for 'Dhis2_Reports_Submissions_Log.submission_id' to match new field type.
        db.rename_column(u'dhis2_attribute_submissions_log', 'submission_id', 'submission_id_id')
        # Changing field 'Dhis2_Reports_Submissions_Log.submission_id'
        db.alter_column(u'dhis2_attribute_submissions_log', 'submission_id_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rapidsms_xforms.XFormSubmission']))

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
        'dhis2.dhis2_reports_submissions_log': {
            'Meta': {'object_name': 'Dhis2_Reports_Submissions_Log', 'db_table': "u'dhis2_attribute_submissions_log'"},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reported_xml': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'submission_id': ('django.db.models.fields.IntegerField', [], {}),
            'task_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dhis2.Dhis2_Reports_Report_Task_Log']"})
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