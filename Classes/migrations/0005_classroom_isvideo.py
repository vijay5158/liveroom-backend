# Generated by Django 4.1.7 on 2023-06-01 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Classes', '0004_alter_classroom_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='isVideo',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
