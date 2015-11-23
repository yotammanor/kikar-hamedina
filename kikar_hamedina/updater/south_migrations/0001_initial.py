# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BaseExecutor'
        db.create_table(u'updater_baseexecutor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'updater', ['BaseExecutor'])

        # Adding model 'TestRule'
        db.create_table(u'updater_testrule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_time_analysed', self.gf('django.db.models.fields.DateTimeField')()),
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

        # Adding model 'TestExecutor'
        db.create_table(u'updater_testexecutor', (
            (u'baseexecutor_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['updater.BaseExecutor'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'updater', ['TestExecutor'])


    def backwards(self, orm):
        # Deleting model 'BaseExecutor'
        db.delete_table(u'updater_baseexecutor')

        # Deleting model 'TestRule'
        db.delete_table(u'updater_testrule')

        # Removing M2M table for field executors on 'TestRule'
        db.delete_table(db.shorten_name(u'updater_testrule_executors'))

        # Deleting model 'TestExecutor'
        db.delete_table(u'updater_testexecutor')


    models = {
        u'updater.baseexecutor': {
            'Meta': {'object_name': 'BaseExecutor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'updater.testexecutor': {
            'Meta': {'object_name': 'TestExecutor', '_ormbases': [u'updater.BaseExecutor']},
            u'baseexecutor_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['updater.BaseExecutor']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'updater.testrule': {
            'Meta': {'object_name': 'TestRule'},
            'executors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['updater.BaseExecutor']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_time_analysed': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['updater']