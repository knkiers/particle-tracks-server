# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-27 00:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AliasName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g., X^+', max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='DecayType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g., X-plus -> mu-plus + Y^0', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Particle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verbose_name', models.CharField(help_text='e.g., K-plus', max_length=40)),
                ('name', models.CharField(help_text='e.g., K^+', max_length=40)),
                ('mass', models.FloatField(help_text='mass in MeV/c^2')),
                ('charge', models.IntegerField(choices=[(1, '+'), (-1, '-'), (0, '0')])),
            ],
        ),
        migrations.AddField(
            model_name='decaytype',
            name='daughter_one',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='decay_types_d1', to='decays.Particle'),
        ),
        migrations.AddField(
            model_name='decaytype',
            name='daughter_one_alias',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='decay_types_d1a', to='decays.AliasName'),
        ),
        migrations.AddField(
            model_name='decaytype',
            name='daughter_one_decay',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='decay_types_d1d', to='decays.DecayType'),
        ),
        migrations.AddField(
            model_name='decaytype',
            name='daughter_three',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='decay_types_d3', to='decays.Particle'),
        ),
        migrations.AddField(
            model_name='decaytype',
            name='daughter_three_alias',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='decay_types_d3a', to='decays.AliasName'),
        ),
        migrations.AddField(
            model_name='decaytype',
            name='daughter_three_decay',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='decay_types_d3d', to='decays.DecayType'),
        ),
        migrations.AddField(
            model_name='decaytype',
            name='daughter_two',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='decay_types_d2', to='decays.Particle'),
        ),
        migrations.AddField(
            model_name='decaytype',
            name='daughter_two_alias',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='decay_types_d2a', to='decays.AliasName'),
        ),
        migrations.AddField(
            model_name='decaytype',
            name='daughter_two_decay',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='decay_types_d2d', to='decays.DecayType'),
        ),
        migrations.AddField(
            model_name='decaytype',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='decay_types', to='decays.Particle'),
        ),
        migrations.AddField(
            model_name='decaytype',
            name='parent_alias',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='decays.AliasName'),
        ),
    ]
