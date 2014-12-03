# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'TestExecutor'
        db.delete_table(u'updater_testexecutor')

        # Deleting model 'TestRule'
        db.delete_table(u'updater_testrule')

        # Removing M2M table for field executors on 'TestRule'
        db.delete_table(db.shorten_name(u'updater_testrule_executors'))

        # Deleting model 'TestExecutor2'
        db.delete_table(u'updater_testexecutor2')


    def backwards(self, orm):
        # Adding model 'TestExecutor'
        db.create_table(u'updater_testexecutor', (
            (u'baseexecutor_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['updater.BaseExecutor'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'updater', ['TestExecutor'])

        # Adding model 'TestRule'
        db.create_table(u'updater_testrule', (
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_updater.testrule_set', null=True, to=orm['contenttypes.ContentType'])),
            ('last_time_analysed', self.gf('django.db.models.fields.DateTimeField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'updater', ['TestRule'])

        # Adding M2M table for field executors on 'TestRule'
        m2m_table_name = db.shorten_name(u'updater_testrule_executors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('testrule', models.ForeignKey(orm[u'updater.testrule'], null=False)),
            ('baseexecutor', models.ForeignKey(orm[u'updater.baseexecutor'], null=False))
        ))
        db.create_unique(m2m_table_name, ['testrule_id', 'baseexecutor_id'])

        # Adding model 'TestExecutor2'
        db.create_table(u'updater_testexecutor2', (
            (u'baseexecutor_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['updater.BaseExecutor'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'updater', ['TestExecutor2'])


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
        u'updater.emailupdater': {
            'Meta': {'object_name': 'EmailUpdater', '_ormbases': [u'updater.BaseExecutor']},
            u'baseexecutor_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['updater.BaseExecutor']", 'unique': 'True', 'primary_key': 'True'}),
            'subscribers': ('jsonfield.fields.JSONField', [], {'default': '[]'})
        },
        u'updater.likesrule': {
            'Meta': {'object_name': 'LikesRule'},
            'executors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['updater.BaseExecutor']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_time_analysed': ('django.db.models.fields.DateTimeField', [], {}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_updater.likesrule_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"})
        }
    }

    complete_apps = ['updater']