# Generated by Django 3.0.3 on 2020-05-09 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dep', '0052_appointmentdoctorpatient_is_reject'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentdoctorpatientoftelemedicine',
            name='is_reject',
            field=models.BooleanField(default=False),
        ),
    ]
