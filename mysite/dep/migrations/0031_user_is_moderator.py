# Generated by Django 3.0.3 on 2020-03-20 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dep', '0030_healthreports'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_moderator',
            field=models.BooleanField(default=False),
        ),
    ]
