# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0003_auto_20160319_2341'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='ignored',
            field=models.BooleanField(default=False),
        ),
    ]
