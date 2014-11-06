# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Facebook_Feed.locally_updated'
        db.add_column(u'facebook_feeds_facebook_feed', 'locally_updated',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(1970, 1, 1, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'Facebook_Status.locally_updated'
        db.add_column(u'facebook_feeds_facebook_status', 'locally_updated',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(1970, 1, 1, 0, 0), blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Facebook_Feed.locally_updated'
        db.delete_column(u'facebook_feeds_facebook_feed', 'locally_updated')

        # Deleting field 'Facebook_Status.locally_updated'
        db.delete_column(u'facebook_feeds_facebook_status', 'locally_updated')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'facebook_feeds.facebook_feed': {
            'Meta': {'ordering': "['feed_type']", 'object_name': 'Facebook_Feed'},
            'about': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'current_fan_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'feed_type': ('django.db.models.fields.CharField', [], {'default': "'PP'", 'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'locally_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'persona': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'feeds'", 'to': u"orm['facebook_feeds.Facebook_Persona']"}),
            'picture_large': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'picture_square': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'requires_user_token': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'username': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'vendor_id': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'})
        },
        u'facebook_feeds.facebook_persona': {
            'Meta': {'object_name': 'Facebook_Persona'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_feed': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'facebook_feeds.facebook_status': {
            'Meta': {'object_name': 'Facebook_Status'},
            'comment_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['facebook_feeds.Facebook_Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_comment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'like_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'locally_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'blank': 'True'}),
            'published': ('django.db.models.fields.DateTimeField', [], {}),
            'share_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'status_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'status_type': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'story': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'story_tags': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'facebook_feeds.facebook_status_attachment': {
            'Meta': {'object_name': 'Facebook_Status_Attachment'},
            'caption': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_object_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'attachment'", 'unique': 'True', 'to': u"orm['facebook_feeds.Facebook_Status']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'})
        },
        u'facebook_feeds.feed_popularity': {
            'Meta': {'ordering': "['-date_of_creation']", 'object_name': 'Feed_Popularity'},
            'date_of_creation': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 26, 0, 0)'}),
            'fan_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['facebook_feeds.Facebook_Feed']"}),
            'followers_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'friends_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'talking_about_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'facebook_feeds.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_for_main_display': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'statuses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'old_tags'", 'symmetrical': 'False', 'to': u"orm['facebook_feeds.Facebook_Status']"})
        },
        u'facebook_feeds.user_token': {
            'Meta': {'object_name': 'User_Token'},
            'date_of_creation': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 26, 0, 0)'}),
            'date_of_expiration': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 12, 25, 0, 0)'}),
            'feeds': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tokens'", 'symmetrical': 'False', 'to': u"orm['facebook_feeds.Facebook_Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'user_id': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['facebook_feeds']