# Generated by Django 3.0.3 on 2020-02-20 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dep', '0010_ratedailyactivities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratedailyactivities',
            name='well_wisher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dep.WellWishers'),
        ),
    ]
