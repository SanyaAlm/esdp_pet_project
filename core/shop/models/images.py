from django.db import models

from core import settings


class Images(models.Model):
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=settings.PRODUCT_IMG_UPLOAD_PATH)
