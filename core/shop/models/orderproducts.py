from django.db import models

from shop.models import Product, Order


class OrderProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_per_product = models.DecimalField(decimal_places=2, max_digits=10)