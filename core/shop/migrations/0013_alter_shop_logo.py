# Generated by Django 3.2.21 on 2023-10-19 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_product_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='logo',
            field=models.ImageField(blank=True, default='default_img/default', null=True, upload_to='logos', verbose_name='Логотип магазина'),
        ),
    ]