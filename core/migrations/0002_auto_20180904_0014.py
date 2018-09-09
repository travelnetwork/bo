# Generated by Django 2.0 on 2018-09-04 00:14

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='picture',
            name='source',
        ),
        migrations.AddField(
            model_name='picture',
            name='uri',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='picture',
            name='id',
            field=models.CharField(default=core.models.default_id, max_length=200, primary_key=True, serialize=False),
        ),
    ]