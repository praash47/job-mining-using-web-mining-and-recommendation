# Generated by Django 3.2.5 on 2021-12-25 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobdetailsextractor', '0003_auto_20211225_0911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='n_vacancy',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='salary',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
