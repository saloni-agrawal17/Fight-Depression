# Generated by Django 3.0.3 on 2020-05-08 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dep', '0049_patient_contact_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='photo_proof',
            field=models.ImageField(null=True, upload_to='images/'),
        ),
    ]