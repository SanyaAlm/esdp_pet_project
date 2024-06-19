from django.contrib import admin
from django.db.models import Sum
from django.utils import timezone

from shop.models import *
from accounts.models import User

# Register your models here.

class ShopInline(admin.StackedInline):
    model = Shop


class MultiModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_name', 'get_phone', 'get_income']

    def get_name(self, obj):
        user = obj.user
        return user.first_name + ' ' + user.last_name

    def get_phone(self, obj):
        user = obj.user
        return user.phone

    def get_income(self, obj):
        orders = Order.objects.filter(shop=obj, is_paid=True)
        income = orders.filter(date=timezone.now()).aggregate(income=Sum('total'))['income']
        return income

    def get_queryset(self, request):
        return Shop.objects.filter(user=request.user)

    def has_delete_permission(self, request, obj=None):
        if request.user.groups.filter(name='Владелец магазина').exists():
            return True
        return False

    def has_add_permission(self, request):
        if request.user.groups.filter(name='Владелец магазина').exists():
            return True
        return False

    def has_module_permission(self, request):
        if request.user.groups.filter(name='Владелец магазина').exists():
            return True
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.groups.filter(name='Владелец магазина').exists():
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name='Владелец магазина').exists():
            return True
        return False

    get_name.short_description = 'ФИО'
    get_phone.short_description = 'Телефон'
    get_income.short_description = 'Доход'


admin.site.register(Shop)
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderProducts)
