# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polyorg', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidatelist',
            name='name',
            field=models.CharField(max_length=80, verbose_name='Name'),
        ),
    ]
