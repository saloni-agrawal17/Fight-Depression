# Generated by Django 3.0.3 on 2020-04-04 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dep', '0041_appointmentdoctorpatientoftelemedicine_doctorsessiontimeoftelemedicine'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='contact_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='doctor',
            name='degree',
            field=models.CharField(default='M.D', max_length=50),
        ),
        migrations.AddField(
            model_name='doctor',
            name='location_of_clinic',
            field=models.CharField(default='bhatar', max_length=100),
        ),
        migrations.AddField(
            model_name='doctor',
            name='telemedicine_facility',
            field=models.CharField(default='no', max_length=10),
        ),
    ]