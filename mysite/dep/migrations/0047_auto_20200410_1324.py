# Generated by Django 3.0.3 on 2020-04-10 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dep', '0046_doctor_reports_needed_for_telemedicine'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctor',
            name='city',
        ),
        migrations.RemoveField(
            model_name='doctor',
            name='state',
        ),
        migrations.AlterField(
            model_name='doctor',
            name='price',
            field=models.IntegerField(null=True),
        ),
    ]
