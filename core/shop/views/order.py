from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import When, Case, IntegerField, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView

from shop.forms import OrderForm
from shop.models import Bucket, Shop, Order, Product, OrderProducts
from .additional_functions import get_client_ip, get_discount


class BucketListView(CreateView):
    template_name = 'orders/bucket.html'
    model = Order
    form_class = OrderForm

    def dispatch(self, request, *args, **kwargs):
        self.user = self.request.user
        self.shop_id = self.kwargs['shop_id']

        try:
            self.bucket_items = Bucket.objects.filter(user=self.user.account, shop_id=self.shop_id)
        except (Bucket.DoesNotExist, AttributeError):
            ip_address = get_client_ip(self.request)
            self.bucket_items = Bucket.objects.filter(ip_address=ip_address, shop_id=self.shop_id)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        self.get_form_data(context)
        for item in self.bucket_items:
            get_discount(item)

        context['bucket'] = self.bucket_items
        context['total_price'] = sum(item.unit_price for item in self.bucket_items)
        context['shop'] = Shop.objects.get(id=self.shop_id)
        context['products'] = {item.product: item for item in self.bucket_items}
        context['items'] = ', '.join(str(item.id) for item in self.bucket_items)

        return context

    def get_form_data(self, context):
        try:
            account = self.user.account
            data = {
                'payer_name': self.user.first_name,
                'payer_surname': self.user.last_name,
                'payer_email': self.user.email,
                'payer_phone': self.user.phone,
                'payer_city': account.city,
                'payer_address': account.address,
                'payer_postal_code': account.postal_code,
            }
            context['form'] = OrderForm(initial=data)
        except AttributeError:
            pass

    def get_success_url(self):
        return reverse_lazy('payment', kwargs={'order_id': self.object.id})


class OrderListView(ListView):
    model = Order
    template_name = 'orders/orders.html'
    context_object_name = 'orders'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = Shop.objects.get(id=self.kwargs['shop_id'])
        return context

    def get_queryset(self):
        try:
            return Order.objects.filter(shop__id=self.kwargs['shop_id'], account=self.request.user.account)
        except AttributeError:
            return Order.objects.filter(shop__id=self.kwargs['shop_id'], user_ip=get_client_ip(self.request))


class ShopOrderListView(ListView, PermissionRequiredMixin):
    model = Order
    template_name = 'profile/shop_orders.html'
    context_object_name = 'orders'

    def dispatch(self, request, *args, **kwargs):
        self.shop = Shop.objects.get(id=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self):
        return self.request.user == self.shop.user

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        return context

    def get_queryset(self):
        queryset = Order.objects.filter(shop__id=self.shop.id)

        if query := self.request.GET.get('search'):
            queryset = queryset.filter(id__icontains=query)
        return queryset


class OrderDetailView(DetailView):
    model = Order
    pk_url_kwarg = 'order_id'
    template_name = 'profile/detail_shop_order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = Shop.objects.get(id=self.kwargs['id'])
        context['orders'] = OrderProducts.objects.filter(order_id=self.kwargs['order_id'])
        return context
