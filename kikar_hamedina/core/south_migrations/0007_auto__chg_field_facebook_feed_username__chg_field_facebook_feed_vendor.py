# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Facebook_Feed', fields ['vendor_id']
        db.delete_unique(u'core_facebook_feed', ['vendor_id'])


        # Changing field 'Facebook_Feed.username'
        db.alter_column(u'core_facebook_feed', 'username', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Facebook_Feed.vendor_id'
        db.alter_column(u'core_facebook_feed', 'vendor_id', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Facebook_Feed.name'
        db.alter_column(u'core_facebook_feed', 'name', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Facebook_Feed.birthday'
        db.alter_column(u'core_facebook_feed', 'birthday', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # Changing field 'Facebook_Feed.username'
        db.alter_column(u'core_facebook_feed', 'username', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Changing field 'Facebook_Feed.vendor_id'
        db.alter_column(u'core_facebook_feed', 'vendor_id', self.gf('django.db.models.fields.CharField')(default='', max_length=128, unique=True))
        # Adding unique constraint on 'Facebook_Feed', fields ['vendor_id']
        db.create_unique(u'core_facebook_feed', ['vendor_id'])


        # Changing field 'Facebook_Feed.name'
        db.alter_column(u'core_facebook_feed', 'name', self.gf('django.db.models.fields.CharField')(max_length=256, null=True))

        # Changing field 'Facebook_Feed.birthday'
        db.alter_column(u'core_facebook_feed', 'birthday', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

    models = {
        u'core.facebook_feed': {
            'Meta': {'object_name': 'Facebook_Feed'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'birthday': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'fan_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'page_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Person']"}),
            'pic_large': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'pic_square': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'talking_about_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'username': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True'}),
            'vendor_id': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'})
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
            'updated': ('django.db.models.fields.DateTimeField', [], {})
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '128'}),
            'statuses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tags'", 'symmetrical': 'False', 'to': u"orm['core.Facebook_Status']"})
        }
    }

    complete_apps = ['core']