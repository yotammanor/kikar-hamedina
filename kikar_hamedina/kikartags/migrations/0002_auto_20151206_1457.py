# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kikartags', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tagsynonym',
            name='tag',
            field=models.OneToOneField(related_name='proper_form_of_tag', to='kikartags.Tag'),
        ),
    ]
