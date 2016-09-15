# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-15 00:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('decays', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalyzedEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(blank=True, default='', max_length=100)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analyzed_events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
