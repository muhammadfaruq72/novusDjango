# Generated by Django 4.1.5 on 2023-02-03 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novus', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='members',
            name='is_admin',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
