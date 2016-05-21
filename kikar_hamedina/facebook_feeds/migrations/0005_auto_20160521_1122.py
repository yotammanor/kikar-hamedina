# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_feeds', '0004_auto_20151207_1858'),
    ]

    operations = [
        migrations.CreateModel(
            name='Facebook_Like',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'like', max_length=32)),
                ('status', models.ForeignKey(related_name='likes', to='facebook_feeds.Facebook_Status')),
                ('user', models.ForeignKey(related_name='likes', to='facebook_feeds.Facebook_User')),
            ],
        ),
        migrations.AlterField(
            model_name='facebook_status_comment',
            name='comment_from',
            field=models.ForeignKey(related_name='comments', to='facebook_feeds.Facebook_User'),
        ),
    ]
