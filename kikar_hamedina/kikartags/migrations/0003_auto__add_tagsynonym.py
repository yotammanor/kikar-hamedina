# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TagSynonym'
        db.create_table(u'kikartags_tagsynonym', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(related_name='synonym_proper_tag', to=orm['kikartags.Tag'])),
            ('synonym_tag', self.gf('django.db.models.fields.related.ForeignKey')(related_name='synonym_synonym_tag', unique=True, to=orm['kikartags.Tag'])),
        ))
        db.send_create_signal(u'kikartags', ['TagSynonym'])


    def backwards(self, orm):
        # Deleting model 'TagSynonym'
        db.delete_table(u'kikartags_tagsynonym')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'kikartags.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_for_main_display': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'kikartags.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'kikartags_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'kikartags_taggeditem_items'", 'to': u"orm['kikartags.Tag']"})
        },
        u'kikartags.tagsynonym': {
            'Meta': {'object_name': 'TagSynonym'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'synonym_tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'synonym_synonym_tag'", 'unique': 'True', 'to': u"orm['kikartags.Tag']"}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'synonym_proper_tag'", 'to': u"orm['kikartags.Tag']"})
        }
    }

    complete_apps = ['kikartags']