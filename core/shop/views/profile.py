from _decimal import Decimal
from datetime import datetime, timedelta

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Sum
from django.utils import timezone
from django.views.generic import DetailView, TemplateView
from accounts.models import User
from shop.models import *


def get_statistics(shops, period, time_period):
    queryset = Order.objects.filter(shop_id__in=shops, is_paid=True)
    orders, income = [], []
    match period:
        case 'year':
            print(queryset)
            print(queryset.filter(date__year=time_period[0]))
            orders = [queryset.filter(date__year=year).count() for year in time_period]
            income = [queryset.filter(date__year=year).aggregate(income=Sum('total'))['income'] for year in time_period]
        case 'month':
            orders = [queryset.filter(date__month=month).count() for month in time_period]
            income = [queryset.filter(date__month=month).aggregate(income=Sum('total'))['income'] for month in
                      time_period]
        case 'day':
            orders = [queryset.filter(date=day).count() for day in time_period]
            income = [queryset.filter(date=day).aggregate(income=Sum('total'))['income'] for day in time_period]

    income = [float(val) if isinstance(val, Decimal) else val for val in income]

    orders = ', '.join(map(str, orders))
    income = ', '.join(map(str, income))
    labels = ', '.join(map(str, time_period))
    return f'{orders}. {income}. {labels}. {period}'


def get_time_period(period, start, end) -> list:
    time_period = []
    match period:
        case 'year':
            start, end = start.year, end.year
            time_period = [year for year in range(start, end + 1)]
        case 'month':
            start, end = start.month, end.month
            time_period = [month for month in range(start, end + 1)] \
                if start <= end else (
                    [month for month in range(start, 13)] + [month for month in range(1, end + 1)])
        case 'day':
            start, end = start, end
            time_period = [(start + timedelta(days=day)).strftime('%Y-%m-%d') for day in range((end - start).days + 1)]
    return time_period


class Profile(PermissionRequiredMixin, DetailView):
    template_name = 'profile/profile.html'
    context_object_name = 'user'
    model = User
    pk_url_kwarg = 'id'

    def has_permission(self):
        return self.request.user == self.get_object()

    def dispatch(self, request, *args, **kwargs):
        self.shops = Shop.objects.filter(user_id=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = datetime.now().month
        months = [12 + month - i if month - i < 1 else month - i for i in range(3, -1, -1)]

        context['shops'] = self.shops
        context['statistics'] = get_statistics(shops=self.shops, period='month', time_period=months)
        return context



class Statistic(PermissionRequiredMixin, TemplateView):
    template_name = 'profile/statistics.html'
    model = User
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        self.user = User.objects.get(id=self.kwargs['id'])
        self.shops = Shop.objects.filter(user=self.user)
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self):
        return self.request.user == User.objects.get(id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shops'] = self.shops
        context['statistics'] = get_statistics(shops=self.stat_shops, period=self.period, time_period=self.time_period)
        return context

    def get(self, request, *args, **kwargs):
        start = datetime.strptime(self.request.GET.get('start_date'), '%Y-%m-%d') if self.request.GET.get(
            'start_date') else timezone.now()
        end = datetime.strptime(self.request.GET.get('end_date'), '%Y-%m-%d') if self.request.GET.get(
            'end_date') else timezone.now()
        self.period = self.request.GET.get('PeriodRadios')

        self.stat_shops = self.shops if self.request.GET.get('shopRadios') == 'all' else Shop.objects.filter(
            id=self.request.GET.get('shopRadios'))

        if start > end:
            start, end = end, start

        self.time_period = get_time_period(self.period, start, end)

        return super().get(request, *args, **kwargs)
