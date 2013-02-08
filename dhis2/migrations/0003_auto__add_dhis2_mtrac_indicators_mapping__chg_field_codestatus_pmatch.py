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
            ('mtrac_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eav.Attribute'])),
            ('dhis2_uuid', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('dhis2_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('dhis2_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('dhis2_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('dhis2_combo_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('dhis2', ['Dhis2_Mtrac_Indicators_Mapping'])


        # Changing field 'CodeStatus.pmatch'
        db.alter_column(u'code_status', 'pmatch', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=3))

    def backwards(self, orm):
        # Deleting model 'Dhis2_Mtrac_Indicators_Mapping'
        db.delete_table(u'dhis2_mtrack_indicators_mapping')


        # Changing field 'CodeStatus.pmatch'
        db.alter_column(u'code_status', 'pmatch', self.gf('django.db.models.fields.DecimalField')(max_digits=65535, decimal_places=3))

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
            'dhis2_combo_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'dhis2_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'dhis2_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'dhis2_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'dhis2_uuid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mtrac_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eav.Attribute']"})
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