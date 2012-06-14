# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'CodeStatus'
        db.create_table(u'code_status', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('facility', self.gf('django.db.models.fields.TextField')()),
            ('ftype', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('created', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_dups', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('fuzzy_matched', self.gf('django.db.models.fields.TextField')()),
            ('dups', self.gf('django.db.models.fields.TextField')()),
            ('pmatch', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=3)),
            ('fid', self.gf('django.db.models.fields.IntegerField')()),
            ('cdate', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('dhis2', ['CodeStatus'])

        # Adding model 'Dhis2Mapping'
        db.create_table(u'dhis2_mapping', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('field_slug', self.gf('django.db.models.fields.TextField')()),
            ('keyword', self.gf('django.db.models.fields.TextField')()),
            ('dhis2_uid', self.gf('django.db.models.fields.TextField')()),
            ('dhis2_type', self.gf('django.db.models.fields.TextField')()),
            ('dhis2_dataelement', self.gf('django.db.models.fields.TextField')()),
            ('cdate', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('dhis2', ['Dhis2Mapping'])


    def backwards(self, orm):

        # Deleting model 'CodeStatus'
        db.delete_table(u'code_status')

        # Deleting model 'Dhis2Mapping'
        db.delete_table(u'dhis2_mapping')


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
