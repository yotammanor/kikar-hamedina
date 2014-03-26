# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User_Token'
        db.create_table(u'core_user_token', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('token', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
            ('user_id', self.gf('django.db.models.fields.TextField')()),
            ('date_of_creation', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 3, 22, 0, 0))),
        ))
        db.send_create_signal(u'core', ['User_Token'])

        # Adding M2M table for field feeds on 'User_Token'
        m2m_table_name = db.shorten_name(u'core_user_token_feeds')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user_token', models.ForeignKey(orm[u'core.user_token'], null=False)),
            ('facebook_feed', models.ForeignKey(orm[u'core.facebook_feed'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_token_id', 'facebook_feed_id'])

        # Adding field 'Facebook_Feed.feed_type'
        db.add_column(u'core_facebook_feed', 'feed_type',
                      self.gf('django.db.models.fields.CharField')(default='PB', max_length=2),
                      keep_default=False)

        # Adding field 'Facebook_Feed.followers_count'
        db.add_column(u'core_facebook_feed', 'followers_count',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Facebook_Feed.friends_count'
        db.add_column(u'core_facebook_feed', 'friends_count',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'User_Token'
        db.delete_table(u'core_user_token')

        # Removing M2M table for field feeds on 'User_Token'
        db.delete_table(db.shorten_name(u'core_user_token_feeds'))

        # Deleting field 'Facebook_Feed.feed_type'
        db.delete_column(u'core_facebook_feed', 'feed_type')

        # Deleting field 'Facebook_Feed.followers_count'
        db.delete_column(u'core_facebook_feed', 'followers_count')

        # Deleting field 'Facebook_Feed.friends_count'
        db.delete_column(u'core_facebook_feed', 'friends_count')


    models = {
        u'core.facebook_feed': {
            'Meta': {'object_name': 'Facebook_Feed'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'birthday': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'fan_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'feed_type': ('django.db.models.fields.CharField', [], {'default': "'PB'", 'max_length': '2'}),
            'followers_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'friends_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'page_url': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Person']"}),
            'pic_large': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True'}),
            'pic_square': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True'}),
            'talking_about_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
            'date_of_creation': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 22, 0, 0)'}),
            'feeds': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tokens'", 'symmetrical': 'False', 'to': u"orm['core.Facebook_Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'user_id': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['core']