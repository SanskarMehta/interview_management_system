# Generated by Django 4.0.5 on 2022-06-17 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_login', '0004_jobopenings_interviewercompany'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterviewerType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=30)),
            ],
        ),
    ]
