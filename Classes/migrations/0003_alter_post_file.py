# Generated by Django 3.2.5 on 2021-07-25 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Classes', '0002_auto_20210721_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='file',
            field=models.FileField(blank=True, upload_to=''),
        ),
    ]