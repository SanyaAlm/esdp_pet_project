# Generated by Django 3.2.21 on 2023-11-24 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_account_postal_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False, verbose_name='Суперпользователь'),
        ),
    ]