# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Feed_Popularity'
        db.create_table(u'core_feed_popularity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Facebook_Feed'])),
            ('date_of_creation', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 4, 1, 0, 0))),
            ('talking_about_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('fan_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('followers_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('friends_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'core', ['Feed_Popularity'])

        # Deleting field 'Facebook_Feed.friends_count'
        db.delete_column(u'core_facebook_feed', 'friends_count')

        # Deleting field 'Facebook_Feed.fan_count'
        db.delete_column(u'core_facebook_feed', 'fan_count')

        # Deleting field 'Facebook_Feed.talking_about_count'
        db.delete_column(u'core_facebook_feed', 'talking_about_count')

        # Deleting field 'Facebook_Feed.followers_count'
        db.delete_column(u'core_facebook_feed', 'followers_count')


    def backwards(self, orm):
        # Deleting model 'Feed_Popularity'
        db.delete_table(u'core_feed_popularity')

        # Adding field 'Facebook_Feed.friends_count'
        db.add_column(u'core_facebook_feed', 'friends_count',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Facebook_Feed.fan_count'
        db.add_column(u'core_facebook_feed', 'fan_count',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Facebook_Feed.talking_about_count'
        db.add_column(u'core_facebook_feed', 'talking_about_count',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Facebook_Feed.followers_count'
        db.add_column(u'core_facebook_feed', 'followers_count',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    models = {
        u'core.facebook_feed': {
            'Meta': {'object_name': 'Facebook_Feed'},
            'about': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'birthday': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'feed_type': ('django.db.models.fields.CharField', [], {'default': "'PP'", 'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'page_url': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Person']"}),
            'pic_large': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True'}),
            'pic_square': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True'}),
            'username': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True'}),
            'vendor_id': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True'})
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
        u'core.feed_popularity': {
            'Meta': {'ordering': "['-date_of_creation']", 'object_name': 'Feed_Popularity'},
            'date_of_creation': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 4, 1, 0, 0)'}),
            'fan_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Facebook_Feed']"}),
            'followers_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'friends_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'talking_about_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_for_main_display': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'statuses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tags'", 'symmetrical': 'False', 'to': u"orm['core.Facebook_Status']"})
        },
        u'core.user_token': {
            'Meta': {'object_name': 'User_Token'},
            'date_of_creation': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 4, 1, 0, 0)'}),
            'date_of_expiration': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 5, 31, 0, 0)'}),
            'feeds': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tokens'", 'symmetrical': 'False', 'to': u"orm['core.Facebook_Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'user_id': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['core']