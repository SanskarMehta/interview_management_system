# Generated by Django 4.0.5 on 2022-07-07 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_login', '0022_remove_reschedulerequests_application_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reschedulerequests',
            name='is_rescheduled',
            field=models.BooleanField(default=False),
        ),
    ]