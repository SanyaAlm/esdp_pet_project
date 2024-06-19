from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from shop.models import Bucket, Product, Shop


# class BucketViewSetTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(email='test@gmail.com', password='testpass', phone=123)
#         self.shop = Shop.objects.create(user_id=self.user.id, name='test')
#         self.product = Product.objects.create(shop_id=self.shop.id, vendor_code=123, price=100)
#
#     def test_add_to_cart(self):
#         client = APIClient()
#
#         response = client.post('/api/bucket/add_to_cart/', {
#             'product': self.product.id,
#             'quantity': 2,
#             'user': self.user.id,
#         }, format='json')
#
#         self.assertEqual(response.status_code, 201)
#         bucket = Bucket.objects.get(user=self.user, product_id=self.product.id)
#         self.assertEqual(bucket.quantity, 2)
#
#     def test_add_to_cart_no_user(self):
#         client = APIClient()
#
#         response = client.post('/api/bucket/add_to_cart/', {
#             'product': self.product.id,
#             'quantity': 3,
#         }, format='json')
#
#         self.assertEqual(response.status_code, 201)
#
#         ip_address = response.json().get('ip_address')
#         bucket = Bucket.objects.get(ip_address=ip_address, product_id=self.product.id)
#         self.assertEqual(bucket.quantity, 3)
