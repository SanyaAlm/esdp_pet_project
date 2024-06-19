from django.db import models


class PartnerProduct(models.Model):
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='partner_product')
    partner_shop = models.ForeignKey('shop.PartnerShop', on_delete=models.CASCADE, related_name='partner_product')
    city = models.ForeignKey('shop.City', on_delete=models.CASCADE, related_name='partner_product')
