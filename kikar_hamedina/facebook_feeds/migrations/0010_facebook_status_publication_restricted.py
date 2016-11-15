# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_feeds', '0009_auto_20160630_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='facebook_status',
            name='publication_restricted',
            field=models.BooleanField(default=False),
        ),
    ]
