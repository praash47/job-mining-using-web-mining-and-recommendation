# Generated by Django 3.2.5 on 2021-12-25 08:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('checkers', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteStructure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=500)),
                ('name_xpath', models.CharField(max_length=1000, null=True)),
                ('deadline_xpath', models.CharField(max_length=1000, null=True)),
                ('company_name_xpath', models.CharField(max_length=1000, null=True)),
                ('company_description_xpath', models.CharField(max_length=1000, null=True)),
                ('location_xpath', models.CharField(max_length=1000, null=True)),
                ('job_description_xpath', models.CharField(max_length=1000, null=True)),
                ('salary_xpath', models.CharField(max_length=1000, null=True)),
                ('no_vacancy_xpath', models.CharField(max_length=1000, null=True)),
                ('level_xpath', models.CharField(max_length=1000, null=True)),
                ('qualification_xpath', models.CharField(max_length=1000, null=True)),
                ('experience_xpath', models.CharField(max_length=1000, null=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checkers.jobwebsite')),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('url', models.CharField(max_length=500)),
                ('deadline', models.DateTimeField(null=True)),
                ('job_skills', models.TextField(null=True)),
                ('company_name', models.TextField(null=True)),
                ('company_info', models.TextField(null=True)),
                ('company_email', models.EmailField(max_length=254, null=True)),
                ('company_location', models.TextField(null=True)),
                ('job_description', models.TextField(null=True)),
                ('salary', models.IntegerField(null=True)),
                ('no_vacancy', models.IntegerField(null=True)),
                ('level', models.TextField(null=True)),
                ('qualification', models.CharField(max_length=150, null=True)),
                ('experience', models.CharField(max_length=500, null=True)),
                ('misc_field', models.TextField(null=True)),
                ('extracted', models.BooleanField(default=False)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checkers.jobwebsite')),
            ],
        ),
    ]
