# Generated by Django 4.1.7 on 2023-07-15 01:26

import Classes.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Classes', '0008_assignment_alter_announcement_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=Classes.models.assign_file_upload_path),
        ),
        migrations.AlterField(
            model_name='assignmentsubmission',
            name='file',
            field=models.FileField(blank=True, upload_to=Classes.models.assign_sub_file_upload_path),
        ),
    ]
