# Generated by Django 3.2 on 2021-04-25 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20210425_1741'),
    ]

    operations = [
        migrations.RenameField(
            model_name='superuser',
            old_name='user_name',
            new_name='username',
        ),
    ]
