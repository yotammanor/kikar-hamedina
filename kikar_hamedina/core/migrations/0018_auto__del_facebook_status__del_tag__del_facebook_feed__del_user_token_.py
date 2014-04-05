# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Facebook_Status'
        db.delete_table(u'core_facebook_status')

        # Deleting model 'Tag'
        db.delete_table(u'core_tag')

        # Removing M2M table for field statuses on 'Tag'
        db.delete_table(db.shorten_name(u'core_tag_statuses'))

        # Deleting model 'Facebook_Feed'
        db.delete_table(u'core_facebook_feed')

        # Deleting model 'User_Token'
        db.delete_table(u'core_user_token')

        # Removing M2M table for field feeds on 'User_Token'
        db.delete_table(db.shorten_name(u'core_user_token_feeds'))

        # Deleting model 'Feed_Popularity'
        db.delete_table(u'core_feed_popularity')

        # Deleting model 'Facebook_Feed_Generic'
        db.delete_table(u'core_facebook_feed_generic')


    def backwards(self, orm):
        # Adding model 'Facebook_Status'
        db.create_table(u'core_facebook_status', (
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Facebook_Feed'])),
            ('comment_count', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('published', self.gf('django.db.models.fields.DateTimeField')()),
            ('share_count', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('status_id', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
            ('like_count', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'core', ['Facebook_Status'])

        # Adding model 'Tag'
        db.create_table(u'core_tag', (
            ('is_for_main_display', self.gf('django.db.models.fields.BooleanField')(default=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
        ))
        db.send_create_signal(u'core', ['Tag'])

        # Adding M2M table for field statuses on 'Tag'
        m2m_table_name = db.shorten_name(u'core_tag_statuses')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tag', models.ForeignKey(orm[u'core.tag'], null=False)),
            ('facebook_status', models.ForeignKey(orm[u'core.facebook_status'], null=False))
        ))
        db.create_unique(m2m_table_name, ['tag_id', 'facebook_status_id'])

        # Adding model 'Facebook_Feed'
        db.create_table(u'core_facebook_feed', (
            ('username', self.gf('django.db.models.fields.TextField')(default=None, null=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=2000, null=True)),
            ('pic_large', self.gf('django.db.models.fields.URLField')(max_length=2000, null=True)),
            ('pic_square', self.gf('django.db.models.fields.URLField')(max_length=2000, null=True)),
            ('vendor_id', self.gf('django.db.models.fields.TextField')(null=True)),
            ('birthday', self.gf('django.db.models.fields.TextField')(null=True)),
            ('feed_type', self.gf('django.db.models.fields.CharField')(default='PP', max_length=2)),
            (u'facebook_feed_generic_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Facebook_Feed_Generic'], unique=True, primary_key=True)),
            ('about', self.gf('django.db.models.fields.TextField')(default='', null=True)),
            ('name', self.gf('django.db.models.fields.TextField')(null=True)),
            ('page_url', self.gf('django.db.models.fields.URLField')(max_length=2000, null=True)),
        ))
        db.send_create_signal(u'core', ['Facebook_Feed'])

        # Adding model 'User_Token'
        db.create_table(u'core_user_token', (
            ('user_id', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('date_of_creation', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 4, 2, 0, 0))),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=256, unique=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_of_expiration', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 6, 1, 0, 0))),
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

        # Adding model 'Feed_Popularity'
        db.create_table(u'core_feed_popularity', (
            ('date_of_creation', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 4, 2, 0, 0))),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Facebook_Feed'])),
            ('followers_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('friends_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('fan_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('talking_about_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'core', ['Feed_Popularity'])

        # Adding model 'Facebook_Feed_Generic'
        db.create_table(u'core_facebook_feed_generic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'core', ['Facebook_Feed_Generic'])


    models = {
        
    }

    complete_apps = ['core']