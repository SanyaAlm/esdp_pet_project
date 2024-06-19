import decimal

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView
from taggit.models import Tag

from shop.forms import ProductForm, ImagesForm
from shop.models import Images, Category, Product, Shop, Bucket, City, PartnerShop
from .additional_functions import get_client_ip
import httpx
from django.http import HttpResponse


class ProductCreateView(PermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/create_product.html'
    extra_context = {
        'image_form': ImagesForm()
    }

    def has_permission(self):
        return Shop.objects.get(id=self.kwargs['shop_id']).user == self.request.user

    def dispatch(self, request, *args, **kwargs):
        self.image_form = ImagesForm()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.image_form = ImagesForm(request.POST, request.FILES)

        if self.image_form.is_valid() and self.get_form().is_valid():
            return self.form_valid(self.get_form())

        return render(self.request, 'product/create_product.html',
                      {'form': self.get_form(), 'image_form': self.image_form})

    def form_valid(self, form):
        shop = get_object_or_404(Shop, id=self.kwargs['shop_id'])
        product = form.save(commit=False)
        product.shop = shop
        product.category = form.cleaned_data['category']

        if product.discount:

            if product.discount > 0:
                product.discounted_price = product.price - (product.price * decimal.Decimal(product.discount / 100))

        self.new_category(product)

        product.save()

        tags_string = form.cleaned_data['tags']
        product.tags.set(tags_string)

        images = self.image_form.cleaned_data['image']

        for image in images:
            Images.objects.create(product=product, image=image)

        return redirect('add_attributes', id=product.id)

    def new_category(self, product):
        if new_category := self.request.POST['new_category']:
            new_category = new_category.capitalize()

            if not Category.objects.filter(name=new_category).exists():
                Category.objects.create(name=new_category)

            product.category = Category.objects.get(name=new_category)
            product.save()

    def form_invalid(self, form):
        return render(self.request, 'product/create_product.html', {'form': form})


class ProductListView(ListView):
    template_name = 'shop/products.html'
    model = Product
    context_object_name = 'products'
    paginate_by = 10
    ordering = ['-created']

    def dispatch(self, request, *args, **kwargs):
        self.shop = get_object_or_404(Shop, id=self.kwargs['shop_id'])
        self.products = self.shop.products.filter(quantity__gt=0)
        return super().dispatch(request, *args, **kwargs)

    def get_allow_empty(self):
        allow_empty = True
        return allow_empty

    def get_queryset(self):
        if query := self.request.GET.get('search'):
            capitalized_query = query.capitalize()
            query = (Q(name__icontains=query) |
                     Q(description__icontains=query) |
                     Q(category__name__icontains=query) |
                     Q(tags__name__icontains=query) |
                     Q(name__icontains=capitalized_query) |
                     Q(description__icontains=capitalized_query) |
                     Q(category__name__icontains=capitalized_query) |
                     Q(tags__name__icontains=query))
            queryset = self.products.filter(query, quantity__gt=0).distinct()
            return queryset

        if category_id := self.request.GET.get('category'):
            return self.shop.products.filter(category_id=category_id, quantity__gt=0)
        return self.products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['now'] = timezone.now()
        context['categories'] = set([products.category for products in self.products])

        return context


class EditProduct(PermissionRequiredMixin, UpdateView):
    template_name = 'product/edit_product.html'
    context_object_name = 'product'
    model = Product
    form_class = ProductForm
    pk_url_kwarg = 'id'

    def has_permission(self):
        return Product.objects.get(id=self.kwargs['id']).shop.user == self.request.user

    def get_success_url(self):
        return reverse('update_attributes', kwargs={'id': self.object.id})

    def dispatch(self, request, *args, **kwargs):
        self.image_form = ImagesForm()
        self.images = self.get_object().images.all()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tags = self.object.tags
        data = {
            'name': self.object.name,
            'description': self.object.description,
            'vendor_code': self.object.vendor_code,
            'quantity': self.object.quantity,
            'price': self.object.price,
            'discount': self.object.discount,
            'tags': '; '.join(tag.name for tag in tags.all()) if tags.exists() else '',
            'category': self.object.category,
        }

        context['form'] = ProductForm(initial=data)
        context['images'] = self.images
        context['shop'] = self.object.shop

        return context

    def new_category(self, product):
        if new_category := self.request.POST['new_category']:
            new_category = new_category.capitalize()

            if not Category.objects.filter(name=new_category).exists():
                Category.objects.create(name=new_category)

            product.category = Category.objects.get(name=new_category)

    def remove_all_tags_without_objects(self):
        for tag in Tag.objects.all():
            if tag.taggit_taggeditem_items.count() == 0:
                tag.delete()

    def save_images(self):
        for image_id, image in self.request.FILES.items():
            old_image = get_object_or_404(Images, id=image_id)
            storage, path = old_image.image.storage, old_image.image.path
            storage.delete(path)
            old_image.image = image
            old_image.save()

    def form_valid(self, form):
        product = form.save(commit=False)

        if product.discount:

            if product.discount > 0:
                product.discounted_price = product.price - (product.price * decimal.Decimal(product.discount / 100))

        self.new_category(product)
        product.save()

        tags_string = form.cleaned_data['tags']
        tags_string = [tag[:-1] if tag[-1] == ';' else tag for tag in tags_string]

        product.tags.set(tags_string)
        self.remove_all_tags_without_objects()

        self.save_images()

        return redirect(self.get_success_url())


class DeleteProduct(PermissionRequiredMixin, DeleteView):
    context_object_name = 'product'
    model = Product
    pk_url_kwarg = 'id'

    def has_permission(self):
        return self.product.shop.user == self.request.user

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, id=self.kwargs['id'])
        self.images = self.product.images.all()
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        for image in self.images:
            storage, path = image.image.storage, image.image.path
            storage.delete(path)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('shop_products', kwargs={'id': self.object.shop_id})


class DetailProduct(DetailView):
    template_name = 'product/detail_product.html'
    context_object_name = 'product'
    model = Product
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        self.product = self.get_object()
        self.shop_id = self.product.shop.id

        try:
            self.bucket_items = Bucket.objects.filter(user=self.request.user.account, shop_id=self.shop_id)
        except AttributeError:
            ip_address = get_client_ip(self.request)
            self.bucket_items = Bucket.objects.filter(ip_address=ip_address, shop_id=self.shop_id)

        self.products = [item.product for item in self.bucket_items]
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['shop'] = self.product.shop
        context['attributes'] = self.product.attributes.all()
        parameters = {}
        for attribute in context['attributes']:
            if ',' in attribute.value:
                parameters[attribute.name] = attribute.value.split(',')
        context['parameters'] = parameters

        context['in_bucket'] = True if self.object in self.products else False
        return context


class ShopProductView(PermissionRequiredMixin, ListView):
    template_name = 'profile/profile_product_list.html'
    context_object_name = 'products'
    model = Product
    pk_url_kwarg = 'id'
    paginate_by = 20

    def has_permission(self):
        return self.shop.user == self.request.user

    def dispatch(self, request, *args, **kwargs):
        self.shop = get_object_or_404(Shop, id=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.shop.products.all()
        if query := self.request.GET.get('search'):
            capitalized_query = query.capitalize()
            query = (Q(name__icontains=query) |
                     Q(description__icontains=query) |
                     Q(category__name__icontains=query) |
                     Q(tags__name__icontains=query) |
                     Q(name__icontains=capitalized_query) |
                     Q(description__icontains=capitalized_query) |
                     Q(category__name__icontains=capitalized_query) |
                     Q(tags__name__icontains=query))
            queryset = queryset.filter(query).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        return context



