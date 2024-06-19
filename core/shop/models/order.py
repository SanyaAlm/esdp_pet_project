from django.db import models



class Order(models.Model):
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='orders', null=True,
                              blank=True)
    user_ip = models.CharField(max_length=100, null=True, blank=True, verbose_name='IP плательщика')
    shop = models.ForeignKey('shop.Shop', on_delete=models.CASCADE, related_name='order')
    products = models.ManyToManyField('shop.Product', related_name='orders', through='OrderProducts')
    total = models.DecimalField(decimal_places=2, max_digits=15, null=False, blank=False, verbose_name='Сумма')
    date = models.DateField(auto_now_add=True)
    payer_name = models.CharField(max_length=150, verbose_name='Имя')
    payer_surname = models.CharField(max_length=150, verbose_name='Фамилия')
    payer_email = models.EmailField(verbose_name='Email')
    payer_phone = models.CharField(max_length=20, verbose_name='Телефон')
    payer_city = models.CharField(max_length=100, verbose_name='Город')
    payer_address = models.CharField(max_length=250, verbose_name='Адрес')
    payer_postal_code = models.CharField(max_length=20, verbose_name='Почтовый индекс')
    is_paid = models.BooleanField(default=False)