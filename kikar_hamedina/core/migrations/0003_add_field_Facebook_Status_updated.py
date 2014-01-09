# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Facebook_Status.updated'
        db.add_column(u'core_facebook_status', 'updated',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(year=1970, month=1, day=1, hour=0)),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Facebook_Status.updated'
        db.delete_column(u'core_facebook_status', 'updated')


    models = {
        u'core.facebook_feed': {
            'Meta': {'object_name': 'Facebook_Feed'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Person']"}),
            'vendor_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        u'core.facebook_status': {
            'Meta': {'object_name': 'Facebook_Status'},
            'comment_count': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Facebook_Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'like_count': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'published': ('django.db.models.fields.DateTimeField', [], {}),
            'share_count': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'status_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': '0'})
        },
        u'core.party': {
            'Meta': {'object_name': 'Party'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'core.person': {
            'Meta': {'object_name': 'Person'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'persons'", 'to': u"orm['core.Party']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'core.tag': {
            'Meta': {'object_name': 'Tag'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '128'}),
            'statuses': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.Facebook_Status']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['core']