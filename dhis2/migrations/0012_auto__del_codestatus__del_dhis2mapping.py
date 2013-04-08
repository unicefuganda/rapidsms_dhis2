# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'CodeStatus'
        db.delete_table(u'code_status')

        # Deleting model 'Dhis2Mapping'
        db.delete_table(u'dhis2_mapping')


    def backwards(self, orm):
        # Adding model 'CodeStatus'
        db.create_table(u'code_status', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('dups', self.gf('django.db.models.fields.TextField')()),
            ('facility', self.gf('django.db.models.fields.TextField')()),
            ('has_dups', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cdate', self.gf('django.db.models.fields.DateTimeField')()),
            ('fuzzy_matched', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pmatch', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=3)),
            ('ftype', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('fid', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('dhis2', ['CodeStatus'])

        # Adding model 'Dhis2Mapping'
        db.create_table(u'dhis2_mapping', (
            ('dhis2_uid', self.gf('django.db.models.fields.TextField')()),
            ('cdate', self.gf('django.db.models.fields.DateTimeField')()),
            ('field_slug', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('keyword', self.gf('django.db.models.fields.TextField')()),
            ('dhis2_dataelement', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('dhis2_type', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('dhis2', ['Dhis2Mapping'])


    models = {
        'dhis2.dhis2_mtrac_indicators_mapping': {
            'Meta': {'object_name': 'Dhis2_Mtrac_Indicators_Mapping', 'db_table': "u'dhis2_mtrack_indicators_mapping'"},
            'dhis2_combo_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'dhis2_uuid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'eav_attribute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eav.Attribute']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
        'eav.attribute': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('site', 'slug'),)", 'object_name': 'Attribute'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'datatype': ('eav.fields.EavDatatypeField', [], {'max_length': '6'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'enum_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eav.EnumGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('eav.fields.EavSlugField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'eav.enumgroup': {
            'Meta': {'object_name': 'EnumGroup'},
            'enums': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['eav.EnumValue']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'eav.enumvalue': {
            'Meta': {'object_name': 'EnumValue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['dhis2']