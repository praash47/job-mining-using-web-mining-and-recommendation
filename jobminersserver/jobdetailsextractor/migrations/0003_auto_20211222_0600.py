# Generated by Django 3.2.5 on 2021-12-22 06:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('checkers', '0004_jobwebsite'),
        ('jobdetailsextractor', '0002_auto_20211222_0501'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteStructure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=500)),
                ('name_xpath', models.CharField(max_length=1000)),
                ('deadline_xpath', models.DateTimeField()),
                ('c_name_xpath', models.CharField(max_length=1000)),
                ('c_information_xpath', models.CharField(max_length=1000)),
                ('email_xpath', models.CharField(max_length=1000)),
                ('location_xpath', models.CharField(max_length=1000)),
                ('job_description_xpath', models.CharField(max_length=1000)),
                ('salary_xpath', models.CharField(max_length=1000)),
                ('no_vacancy_xpath', models.CharField(max_length=1000)),
                ('level_xpath', models.CharField(max_length=1000)),
                ('qualification_xpath', models.CharField(max_length=1000)),
                ('experience_xpath', models.CharField(max_length=1000)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checkers.jobwebsite')),
            ],
        ),
        migrations.DeleteModel(
            name='JobWebsiteStrucutre',
        ),
        migrations.AlterField(
            model_name='job',
            name='website',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checkers.jobwebsite'),
        ),
    ]
