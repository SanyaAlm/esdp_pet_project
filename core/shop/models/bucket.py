from django.db import models

from accounts.models import User, Account
from shop.models import Product, Shop


class Bucket(models.Model):
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='shop'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_in_bucket'
    )
    quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name='Количество'
    )
    unit_price = models.DecimalField(
        decimal_places=2,
        max_digits=13,
        null=True,
        blank=True,
        default=0,
        verbose_name='Цена за единицу'
    )
    user = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='bucket_user'
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )
