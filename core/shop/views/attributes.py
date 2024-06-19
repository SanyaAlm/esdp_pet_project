from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView
from shop.models import Attributes, Product


class AttributesCreateView(PermissionRequiredMixin, CreateView):
    model = Attributes
    template_name = 'product/add_attributes.html'
    fields = ['name', 'value']

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, id=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)
    def has_permission(self):
        return self.product.shop.user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.product.shop
        return context

    def post(self, request, *args, **kwargs):
        data = dict(zip(request.POST.getlist('name'), request.POST.getlist('value')))

        for name, value in data.items():
            Attributes.objects.create(product=self.product, name=name, value=value)

        return redirect('shop_products', id=self.product.shop_id)


class AttributesUpdateView(PermissionRequiredMixin, UpdateView):
    model = Attributes
    template_name = 'product/edit_attributes.html'
    fields = ['name', 'value']
    pk_url_kwarg = 'id'
    object = None

    def has_permission(self):
        return self.product.shop.user == self.request.user

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, id=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attributes'] = self.get_queryset()
        return context

    def get_queryset(self):
        if Attributes.objects.filter(product=self.product).exists():
            return Attributes.objects.filter(product=self.product)
        return None

    def get(self, request, *args, **kwargs):
        if not self.get_queryset():
            return redirect('add_attributes', id=self.product.id)
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        data = dict(zip(request.POST.getlist('name'), request.POST.getlist('value')))

        for name, value in data.items():
            Attributes.objects.update_or_create(product=self.product, name=name, value=value)

        self.delete_unused_attributes(data)

        return redirect('shop_products', id=self.product.shop_id)

    def delete_unused_attributes(self, data):
        for attribute in self.get_queryset():
            if attribute.name not in data:
                attribute.delete()
