# Generated by Django 4.1.7 on 2023-06-01 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0002_remove_customuser_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='face_template',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
