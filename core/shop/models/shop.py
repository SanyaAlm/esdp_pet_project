from django.db import models
from django.db.models import TextChoices

from core import settings
from taggit.managers import TaggableManager


class Themes(TextChoices):
    DARK = 'black', 'Темная'
    LIGHT = 'white', 'Светлая'
    BLUE = 'blue', 'Синяя'


class Shop(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='shop',
        verbose_name='Владелец магазина',
    )
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        verbose_name='Название магазина',
        unique=True
    )
    logo = models.ImageField(
        null=True,
        blank=True,
        upload_to=settings.LOGO_IMG_UPLOAD_PATH,
        verbose_name='Логотип магазина',
        default='def.png'
    )

    description = models.TextField(
        null=True,
        blank=True,
        max_length=2500,
        verbose_name='Описание магазина'
    )

    theme = models.CharField(
        max_length=255,
        choices=Themes.choices,
        default=Themes.DARK,
        verbose_name='Тема магазина'
    )

    partner_id = models.CharField(
        max_length=255,
        verbose_name='ID Партнера(Kaspi)',
        blank=True,
        null=True,
        unique=True
    )

    tg_token = models.CharField(
        max_length=255,
        verbose_name='Телеграм-токен',
        blank=True,
        null=True,
        unique=True
    )

    tags = TaggableManager(blank=True, verbose_name='Тэги')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
