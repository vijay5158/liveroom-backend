# Generated by Django 4.1.7 on 2023-07-15 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Classes', '0011_assignmentsubmission_remarks'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='title',
            field=models.CharField(default='', max_length=500),
        ),
    ]