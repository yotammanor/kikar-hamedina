# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('kikartags', '0001_initial'),
        ('facebook_feeds', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Facebook_Status_Comment',
            fields=[
                ('comment_id', models.CharField(max_length=128, unique=True, serialize=False, primary_key=True)),
                ('content', models.TextField()),
                ('like_count', models.PositiveIntegerField(default=0, blank=True)),
                ('comment_count', models.PositiveIntegerField(default=0, blank=True)),
                ('published', models.DateTimeField()),
                ('message_tags', models.TextField(null=True, blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('locally_updated', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), blank=True)),
            ],
            options={
                'verbose_name_plural': 'Facebook_Status_Comments',
            },
        ),
        migrations.CreateModel(
            name='Facebook_Status_Comment_Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('caption', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('link', models.TextField()),
                ('facebook_object_id', models.CharField(max_length=128, null=True, blank=True)),
                ('type', models.CharField(max_length=16, null=True, blank=True)),
                ('picture', models.TextField(null=True, blank=True)),
                ('source', models.TextField(null=True, blank=True)),
                ('source_width', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('source_height', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('status', models.OneToOneField(related_name='attachment', to='facebook_feeds.Facebook_Status_Comment')),
            ],
        ),
        migrations.CreateModel(
            name='Facebook_User',
            fields=[
                ('facebook_id', models.CharField(max_length=32, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=254, null=True, blank=True)),
                ('type', models.CharField(max_length=32, null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='facebook_status_comment',
            name='comment_from',
            field=models.ForeignKey(to='facebook_feeds.Facebook_User'),
        ),
        migrations.AddField(
            model_name='facebook_status_comment',
            name='parent',
            field=models.ForeignKey(to='facebook_feeds.Facebook_Status'),
        ),
        migrations.AddField(
            model_name='facebook_status_comment',
            name='tags',
            field=taggit.managers.TaggableManager(to='kikartags.Tag', through='kikartags.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
    ]
