# Generated by Django 3.2 on 2021-04-25 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20210425_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='photo',
            field=models.BinaryField(default=None, null=True, verbose_name='Photo'),
        ),
    ]
