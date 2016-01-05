# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='name_ar',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='name_en',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='name_he',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='party',
            name='name_ar',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='party',
            name='name_en',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='party',
            name='name_he',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
