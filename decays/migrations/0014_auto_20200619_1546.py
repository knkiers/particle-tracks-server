# Generated by Django 3.0.6 on 2020-06-19 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('decays', '0013_auto_20200619_1538'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='decaytype',
            name='human_readable_name',
        ),
        migrations.RemoveField(
            model_name='decaytype',
            name='name',
        ),
    ]
