# Generated by Django 3.0.3 on 2020-03-09 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dep', '0019_auto_20200309_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentdoctorpatient',
            name='slot_time2_to',
            field=models.TimeField(null=True),
        ),
    ]