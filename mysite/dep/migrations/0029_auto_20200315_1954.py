# Generated by Django 3.0.3 on 2020-03-15 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dep', '0028_auto_20200310_1754'),
    ]

    operations = [
        migrations.RenameField(
            model_name='connectionpatientwellwishers',
            old_name='p_userid',
            new_name='patient',
        ),
    ]