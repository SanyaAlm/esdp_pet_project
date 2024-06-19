from django.db import models


class TimeDiscount(models.Model):
    product = models.OneToOneField('shop.Product', on_delete=models.CASCADE, related_name='time_discount')
    discount = models.PositiveIntegerField(null=True, blank=True)
    discount_in_currency = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    discounted_price = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=10)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
