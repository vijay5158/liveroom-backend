# Generated by Django 3.2.5 on 2021-07-21 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Classes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classroom',
            name='Class_name',
        ),
        migrations.DeleteModel(
            name='Class',
        ),
    ]
