from django.contrib import admin
from shop.models import Shop


# Register your models here.
class ShopInline(admin.StackedInline):
    model = Shop


class MultiModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_name', 'get_phone']

    def get_name(self, obj):
        user = obj.user
        return user.first_name + ' ' + user.last_name

    def get_phone(self, obj):
        user = obj.user
        return user.phone

    get_name.short_description = 'Имя'
    get_phone.short_description = 'Телефон'


# admin.site.register(Shop, MultiModelAdmin)
