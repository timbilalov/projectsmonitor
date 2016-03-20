# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_site_moved_to_external'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 19, 20, 40, 47, 266896, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='site',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 19, 20, 41, 2, 426673, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
