# Generated by Django 3.2.21 on 2023-11-21 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0034_auto_20231121_2328'),
        ('accounts', '0009_auto_20231121_2328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='shops',
            field=models.ManyToManyField(related_name='shops', through='shop.AccountShops', to='shop.Shop', verbose_name='Магазины'),
        ),
        migrations.AlterField(
            model_name='account',
            name='token',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Токен'),
        ),
    ]