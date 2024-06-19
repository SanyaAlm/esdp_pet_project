from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100)
    city_code = models.IntegerField()

    def __str__(self):
        return f'{self.name}'
