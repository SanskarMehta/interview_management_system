# Generated by Django 4.0.5 on 2022-06-17 08:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_login', '0003_userdetails'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobOpenings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_location', models.CharField(max_length=50)),
                ('job_role', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=300)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InterviewerCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company', to=settings.AUTH_USER_MODEL)),
                ('interviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interview', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
