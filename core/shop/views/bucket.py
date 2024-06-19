from django.views.generic import ListView

from shop.models import Bucket, Shop, Product


class BucketListView(ListView):
    template_name = 'shop/bucket.html'
    model = Bucket
    context_object_name = 'bucket'
    extra_context = {
        'shops': Shop.objects.all(),
    }

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            bucket_items = Bucket.objects.filter(user=user.id)
        else:
            ip_address = self.get_client_ip(self.request)
            bucket_items = Bucket.objects.filter(ip_address=ip_address)

        total_price_by_shop = {}

        for item in bucket_items:
            item.unit_price = item.product.price * item.quantity
            shop_name = item.product.shop.name
            total_price_by_shop[shop_name] = total_price_by_shop.get(shop_name, 0) + item.unit_price

        context['total_price'] = sum(item.unit_price for item in bucket_items)
        context['bucket'] = bucket_items
        context['total_price_by_shop'] = total_price_by_shop

        return context

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        return ip



