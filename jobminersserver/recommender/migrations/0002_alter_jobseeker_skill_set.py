# Generated by Django 3.2.5 on 2021-12-30 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recommender", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jobseeker",
            name="skill_set",
            field=models.TextField(null=True),
        ),
    ]
