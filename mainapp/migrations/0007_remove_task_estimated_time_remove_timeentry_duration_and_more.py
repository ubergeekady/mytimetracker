# Generated by Django 4.0 on 2021-12-21 23:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_alter_task_estimated_time_alter_timeentry_duration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='estimated_time',
        ),
        migrations.RemoveField(
            model_name='timeentry',
            name='duration',
        ),
        migrations.AddField(
            model_name='task',
            name='durationhours',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(500)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='durationminutes',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(60)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='timeentry',
            name='durationminutes',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(60)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='timeentry',
            name='durationseconds',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(60)]),
            preserve_default=False,
        ),
    ]