from django.urls import path
from .views import *
urlpatterns = [
    path('', ShopListView.as_view(), name='home'),
    path('shop/<int:shop_id>', ShopMainView.as_view(), name='shop_view'),
    path('create/', ShopCreateView.as_view(), name='shop_create'),
    path('update/<int:id>', ShopUpdateView.as_view(), name='shop_update'),
    path('delete/<int:id>', ShopDeleteView.as_view(), name='shop_delete'),
    path('shop/catalog', shop.ShopCatalogView.as_view(), name='shop_catalog'),

    path('shop/<int:shop_id>/create_product/', ProductCreateView.as_view(), name='create_product'),
    path('shop/<int:shop_id>/products/', ProductListView.as_view(), name='shop_products'),
    path('product/<int:id>', DetailProduct.as_view(), name='detail_product'),
    path('product/<int:id>/edit/', EditProduct.as_view(), name='edit_product'),
    path('product/<int:id>/delete/', DeleteProduct.as_view(), name='delete_product'),
    path('product/<int:id>/attributes/add/', AttributesCreateView.as_view(), name='add_attributes'),
    path('product/<int:id>/attributes/update/', AttributesUpdateView.as_view(), name='update_attributes'),

    path('profile/<int:id>/', Profile.as_view(), name='profile'),
    path('profile/<int:id>/statistic/', Statistic.as_view(), name='statistic'),
    path('profile/shop/<int:id>/products/', ShopProductView.as_view(), name='shop_products'),
    path('profile/shop/<int:id>/orders/', ShopOrderListView.as_view(), name='shop_orders'),
    path('profile/shop/<int:id>/orders/<int:order_id>/', OrderDetailView.as_view(), name='detail_order'),

    path('shop/<int:shop_id>/cart/', BucketListView.as_view(), name='bucket'),
    path('shop/<int:shop_id>/orders/', OrderListView.as_view(), name='orders'),
    path('pay/', Pay.as_view(), name='success_payment')

]

