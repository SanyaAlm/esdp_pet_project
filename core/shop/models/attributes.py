from django.db import models


class Attributes(models.Model):
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=100, blank=False, null=False)
    value = models.CharField(max_length=100)