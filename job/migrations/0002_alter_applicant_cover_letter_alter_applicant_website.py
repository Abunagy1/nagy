# Generated by Django 4.1.4 on 2023-01-20 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicant',
            name='cover_letter',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='website',
            field=models.URLField(blank=True),
        ),
    ]
