# Generated by Django 3.0.3 on 2020-03-31 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dep', '0039_patienttreatmentandmedicineinfo_timestamp'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='connectionpatientwellwishers',
            options={'ordering': ['patient']},
        ),
        migrations.AddField(
            model_name='patient',
            name='date_of_birth',
            field=models.DateField(null=True),
        ),
    ]
