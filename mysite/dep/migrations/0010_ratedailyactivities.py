# Generated by Django 3.0.3 on 2020-02-20 07:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dep', '0009_auto_20200216_2304'),
    ]

    operations = [
        migrations.CreateModel(
            name='RateDailyActivities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('q1', models.IntegerField()),
                ('q2', models.IntegerField()),
                ('q3', models.IntegerField()),
                ('q4', models.IntegerField()),
                ('q5', models.IntegerField()),
                ('q6', models.IntegerField()),
                ('q7', models.IntegerField()),
                ('q8', models.IntegerField()),
                ('q9', models.IntegerField()),
                ('q10', models.IntegerField()),
                ('q11', models.IntegerField()),
                ('q12', models.IntegerField()),
                ('date', models.DateField(auto_now_add=True)),
                ('total', models.IntegerField()),
                ('p_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dep.Patient')),
                ('well_wisher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dep.ConnectionPatientWellWishers')),
            ],
        ),
    ]