from django.db import models


class AccountShops(models.Model):
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='shop_account')
    shop = models.ForeignKey('shop.Shop', on_delete=models.CASCADE, related_name='account_shops')
