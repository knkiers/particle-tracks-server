# Generated by Django 3.0.6 on 2020-06-19 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decays', '0012_auto_20200619_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decaytype',
            name='human_readable_name',
            field=models.CharField(blank=True, default='', help_text='e.g., X-plus -> mu-plus + Y^0', max_length=200),
        ),
        migrations.AlterField(
            model_name='decaytype',
            name='name',
            field=models.CharField(blank=True, default='', help_text='e.g., X<sup>0</sup> &rarr;  &pi;<sup>+</sup> + &pi;<sup>-</sup>, but written with sup and ampersands, etc.', max_length=200),
        ),
    ]
