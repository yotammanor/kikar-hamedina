# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LinkType'
        db.create_table(u'links_linktype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'links', ['LinkType'])

        # Adding model 'Link'
        db.create_table(u'links_link', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=1000)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='content_type_set_for_link', to=orm['contenttypes.ContentType'])),
            ('object_pk', self.gf('django.db.models.fields.TextField')()),
            ('link_type', self.gf('django.db.models.fields.related.ForeignKey')(default='', to=orm['links.LinkType'], null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'links', ['Link'])

        # Adding model 'LinkedFile'
        db.create_table(u'links_linkedfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('link', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['links.Link'], null=True, blank=True)),
            ('sha1', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('link_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'links', ['LinkedFile'])


    def backwards(self, orm):
        # Deleting model 'LinkType'
        db.delete_table(u'links_linktype')

        # Deleting model 'Link'
        db.delete_table(u'links_link')

        # Deleting model 'LinkedFile'
        db.delete_table(u'links_linkedfile')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'links.link': {
            'Meta': {'object_name': 'Link'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_link'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_type': ('django.db.models.fields.related.ForeignKey', [], {'default': "''", 'to': u"orm['links.LinkType']", 'null': 'True', 'blank': 'True'}),
            'object_pk': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '1000'})
        },
        u'links.linkedfile': {
            'Meta': {'object_name': 'LinkedFile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['links.Link']", 'null': 'True', 'blank': 'True'}),
            'link_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'sha1': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'})
        },
        u'links.linktype': {
            'Meta': {'object_name': 'LinkType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['links']