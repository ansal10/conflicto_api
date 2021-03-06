# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-20 21:42
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conflicto', '0001_initial'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='reaction',
            name='conflicto_r_object__242a40_idx',
        ),
        migrations.RemoveField(
            model_name='reaction',
            name='action',
        ),
        migrations.AddField(
            model_name='reaction',
            name='actions',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=[], max_length=255),
        ),
        migrations.AddIndex(
            model_name='reaction',
            index=models.Index(fields=['object_uuid', 'object_type', 'user_id'], name='conflicto_r_object__c0c22f_idx'),
        ),
    ]
