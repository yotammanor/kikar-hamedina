# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_feeds', '0005_auto_20160521_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facebook_status_comment',
            name='parent',
            field=models.ForeignKey(related_name='comments', to='facebook_feeds.Facebook_Status'),
        ),
    ]
