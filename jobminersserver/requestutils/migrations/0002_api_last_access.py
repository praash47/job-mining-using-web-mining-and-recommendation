# Generated by Django 3.2.5 on 2021-08-09 14:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('requestutils', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='api',
            name='last_access',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]