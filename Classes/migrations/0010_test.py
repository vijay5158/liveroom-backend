# Generated by Django 3.2.6 on 2021-09-08 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Classes', '0009_announcement_classroom'),
    ]

    operations = [
        migrations.CreateModel(
            name='test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_file', models.FileField(blank=True, upload_to='')),
            ],
        ),
    ]
