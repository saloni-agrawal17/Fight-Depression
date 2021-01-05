# Generated by Django 3.0.3 on 2020-05-08 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dep', '0050_doctor_photo_proof'),
    ]

    operations = [
        migrations.RenameField(
            model_name='doctor',
            old_name='price',
            new_name='fees_for_clinic_patient',
        ),
        migrations.AddField(
            model_name='doctor',
            name='fees_for_telemedicine_patient',
            field=models.IntegerField(null=True),
        ),
    ]
