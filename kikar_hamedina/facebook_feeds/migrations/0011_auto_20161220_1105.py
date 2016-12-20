# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_feeds', '0010_facebook_status_publication_restricted'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='facebook_status',
            options={'get_latest_by': 'published', 'verbose_name_plural': 'Facebook_Statuses'},
        ),
    ]
