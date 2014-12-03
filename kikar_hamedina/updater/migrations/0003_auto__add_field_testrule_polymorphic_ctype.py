# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TestRule.polymorphic_ctype'
        db.add_column(u'updater_testrule', 'polymorphic_ctype',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_updater.testrule_set', null=True, to=orm['contenttypes.ContentType']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TestRule.polymorphic_ctype'
        db.delete_column(u'updater_testrule', 'polymorphic_ctype_id')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'updater.baseexecutor': {
            'Meta': {'object_name': 'BaseExecutor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_updater.baseexecutor_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"})
        },
        u'updater.testexecutor': {
            'Meta': {'object_name': 'TestExecutor', '_ormbases': [u'updater.BaseExecutor']},
            u'baseexecutor_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['updater.BaseExecutor']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'updater.testrule': {
            'Meta': {'object_name': 'TestRule'},
            'executors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['updater.BaseExecutor']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_time_analysed': ('django.db.models.fields.DateTimeField', [], {}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_updater.testrule_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"})
        }
    }

    complete_apps = ['updater']