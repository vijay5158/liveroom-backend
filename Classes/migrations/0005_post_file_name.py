# Generated by Django 3.2.5 on 2021-07-27 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Classes', '0004_alter_post_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='file_name',
            field=models.CharField(default='', max_length=500),
        ),
    ]
