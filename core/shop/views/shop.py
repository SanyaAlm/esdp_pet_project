from urllib.parse import urlencode

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, ListView, DeleteView

from accounts.forms import LoginForm
from shop.forms import ShopModelForm, SearchForm
from shop.models import Shop, Product, Bucket
from django.urls import reverse_lazy


class ShopCreateView(LoginRequiredMixin, CreateView):
    model = Shop
    template_name = 'shop/shop_create_update.html'
    form_class = ShopModelForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'id': self.request.user.id})


class ShopUpdateView(PermissionRequiredMixin, UpdateView):
    model = Shop
    template_name = 'shop/shop_update.html'
    form_class = ShopModelForm
    context_object_name = 'shop'
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        self.shop = get_object_or_404(Shop, id=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self):
        return self.shop.user == self.request.user

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'id': self.request.user.id})


class ShopListView(ListView):
    template_name = 'main.html'
    model = Shop
    context_object_name = 'shops'
    paginate_by = 3
    extra_context = {
        'form': LoginForm(),
        "products": Product.objects.all(),
        'bucket': Bucket.objects.all()
    }

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        bucket_items = Bucket.objects.filter(user=user.id)
        for item in bucket_items:
            item.unit_price = item.product.price * item.quantity
        total_price = sum(item.unit_price for item in bucket_items)

        context['total_price'] = total_price

        return context


class ShopCatalogView(ListView):
    template_name = 'shop/catalog.html'
    model = Shop
    context_object_name = 'shops'
    paginate_by = 9

    def dispatch(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.search_value = self.get_search_value()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        if self.search_value:
            context['query'] = urlencode({'search': self.search_value})

        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if self.search_value:
            query = Q(name__icontains=self.search_value)
            qs = qs.filter(query)

        return qs

    def get_search_form(self):
        return SearchForm(self.request.GET)

    def get_search_value(self):
        if self.form.is_valid():
            return self.form.cleaned_data.get('search')


class ShopDeleteView(PermissionRequiredMixin, DeleteView):
    model = Shop
    pk_url_kwarg = 'id'

    def has_permission(self):
        return self.shop.user == self.request.user

    def dispatch(self, request, *args, **kwargs):
        self.shop = get_object_or_404(Shop, id=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        old_logo = self.shop.logo
        storage, path = old_logo.storage, old_logo.path
        storage.delete(path)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'id': self.request.user.id})


class ShopMainView(ListView):
    template_name = 'shop/shop_main.html'
    model = Product
    context_object_name = 'products'

    def dispatch(self, request, *args, **kwargs):
        self.shop = get_object_or_404(Shop, id=self.kwargs['shop_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.shop.products.filter(quantity__gt=0)
        categories = set([products.category for products in products])
        category_product = {}
        context['shop'] = self.shop
        context['products'] = products[:3]
        context['now'] = timezone.now()

        for category in categories:
            category_product[category] = products.filter(category=category)[:3]
        context['category_product'] = category_product

        return context
