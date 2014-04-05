# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Facebook_Feed_Generic'
        db.create_table(u'facebook_feeds_facebook_feed_generic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'facebook_feeds', ['Facebook_Feed_Generic'])

        # Adding model 'Facebook_Feed'
        db.create_table(u'facebook_feeds_facebook_feed', (
            (u'facebook_feed_generic_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['facebook_feeds.Facebook_Feed_Generic'], unique=True, primary_key=True)),
            ('vendor_id', self.gf('django.db.models.fields.TextField')(null=True)),
            ('username', self.gf('django.db.models.fields.TextField')(default=None, null=True)),
            ('birthday', self.gf('django.db.models.fields.TextField')(null=True)),
            ('name', self.gf('django.db.models.fields.TextField')(null=True)),
            ('page_url', self.gf('django.db.models.fields.URLField')(max_length=2000, null=True)),
            ('pic_large', self.gf('django.db.models.fields.URLField')(max_length=2000, null=True)),
            ('pic_square', self.gf('django.db.models.fields.URLField')(max_length=2000, null=True)),
            ('feed_type', self.gf('django.db.models.fields.CharField')(default='PP', max_length=2)),
            ('about', self.gf('django.db.models.fields.TextField')(default='', null=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=2000, null=True)),
        ))
        db.send_create_signal(u'facebook_feeds', ['Facebook_Feed'])

        # Adding model 'Feed_Popularity'
        db.create_table(u'facebook_feeds_feed_popularity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['facebook_feeds.Facebook_Feed'])),
            ('date_of_creation', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 4, 5, 0, 0))),
            ('talking_about_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('fan_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('followers_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('friends_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'facebook_feeds', ['Feed_Popularity'])

        # Adding model 'Facebook_Status'
        db.create_table(u'facebook_feeds_facebook_status', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['facebook_feeds.Facebook_Feed'])),
            ('status_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('like_count', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('comment_count', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('share_count', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('published', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'facebook_feeds', ['Facebook_Status'])

        # Adding model 'User_Token'
        db.create_table(u'facebook_feeds_user_token', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('token', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
            ('user_id', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('date_of_creation', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 4, 5, 0, 0))),
            ('date_of_expiration', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 6, 4, 0, 0))),
        ))
        db.send_create_signal(u'facebook_feeds', ['User_Token'])

        # Adding M2M table for field feeds on 'User_Token'
        m2m_table_name = db.shorten_name(u'facebook_feeds_user_token_feeds')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user_token', models.ForeignKey(orm[u'facebook_feeds.user_token'], null=False)),
            ('facebook_feed', models.ForeignKey(orm[u'facebook_feeds.facebook_feed'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_token_id', 'facebook_feed_id'])

        # Adding model 'Tag'
        db.create_table(u'facebook_feeds_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('is_for_main_display', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'facebook_feeds', ['Tag'])

        # Adding M2M table for field statuses on 'Tag'
        m2m_table_name = db.shorten_name(u'facebook_feeds_tag_statuses')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tag', models.ForeignKey(orm[u'facebook_feeds.tag'], null=False)),
            ('facebook_status', models.ForeignKey(orm[u'facebook_feeds.facebook_status'], null=False))
        ))
        db.create_unique(m2m_table_name, ['tag_id', 'facebook_status_id'])


    def backwards(self, orm):
        # Deleting model 'Facebook_Feed_Generic'
        db.delete_table(u'facebook_feeds_facebook_feed_generic')

        # Deleting model 'Facebook_Feed'
        db.delete_table(u'facebook_feeds_facebook_feed')

        # Deleting model 'Feed_Popularity'
        db.delete_table(u'facebook_feeds_feed_popularity')

        # Deleting model 'Facebook_Status'
        db.delete_table(u'facebook_feeds_facebook_status')

        # Deleting model 'User_Token'
        db.delete_table(u'facebook_feeds_user_token')

        # Removing M2M table for field feeds on 'User_Token'
        db.delete_table(db.shorten_name(u'facebook_feeds_user_token_feeds'))

        # Deleting model 'Tag'
        db.delete_table(u'facebook_feeds_tag')

        # Removing M2M table for field statuses on 'Tag'
        db.delete_table(db.shorten_name(u'facebook_feeds_tag_statuses'))


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'facebook_feeds.facebook_feed': {
            'Meta': {'ordering': "['feed_type']", 'object_name': 'Facebook_Feed', '_ormbases': [u'facebook_feeds.Facebook_Feed_Generic']},
            'about': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'birthday': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'facebook_feed_generic_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['facebook_feeds.Facebook_Feed_Generic']", 'unique': 'True', 'primary_key': 'True'}),
            'feed_type': ('django.db.models.fields.CharField', [], {'default': "'PP'", 'max_length': '2'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'page_url': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True'}),
            'pic_large': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True'}),
            'pic_square': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True'}),
            'username': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True'}),
            'vendor_id': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'null': 'True'})
        },
        u'facebook_feeds.facebook_feed_generic': {
            'Meta': {'object_name': 'Facebook_Feed_Generic'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'facebook_feeds.facebook_status': {
            'Meta': {'object_name': 'Facebook_Status'},
            'comment_count': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['facebook_feeds.Facebook_Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'like_count': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'published': ('django.db.models.fields.DateTimeField', [], {}),
            'share_count': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'status_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'facebook_feeds.feed_popularity': {
            'Meta': {'ordering': "['-date_of_creation']", 'object_name': 'Feed_Popularity'},
            'date_of_creation': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 4, 5, 0, 0)'}),
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
            'statuses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tags'", 'symmetrical': 'False', 'to': u"orm['facebook_feeds.Facebook_Status']"})
        },
        u'facebook_feeds.user_token': {
            'Meta': {'object_name': 'User_Token'},
            'date_of_creation': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 4, 5, 0, 0)'}),
            'date_of_expiration': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 4, 0, 0)'}),
            'feeds': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tokens'", 'symmetrical': 'False', 'to': u"orm['facebook_feeds.Facebook_Feed']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'user_id': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['facebook_feeds']