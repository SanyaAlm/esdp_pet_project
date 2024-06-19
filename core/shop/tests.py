from django.urls import reverse
from django.test import TestCase, Client

from accounts.models import User

from .models import Shop, Product
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile


class ShopCreateCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email='myemail@gmail.com', phone='77014779047', password='123')

    def test_shop_creation(self) -> None:
        self.client.login(username='myemail@gmail.com', password='123')

        response = self.client.post(reverse('shop_create'), {
            'name': 'New',
            'description': 'Test description',
            'theme': 'black'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Shop.objects.count(), 1)
        new_shop = Shop.objects.first()
        self.assertEqual(new_shop.user, self.user)
        self.assertRedirects(response, reverse('profile', kwargs={'id': self.user.id}))

    def test_shop_created_invalid(self) -> None:
        self.client.login(username='myemail@gmail.com', password='123')
        response = self.client.post(reverse('shop_create'), {
            'name': 'New',
            'description': 'Test description',
            'theme': 'greeen'
        })

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Выберите корректный вариант. greeen нет среди допустимых значений.')


class ShopUpdateCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email='myemail@gmail.com', phone='77014779047', password='123')
        self.shop = Shop.objects.create(user_id=self.user.id, name='New', description='Test description', theme='black')

    def test_update_success(self) -> None:
        self.client.login(username='myemail@gmail.com', password='123')
        response = self.client.post(reverse('shop_update', kwargs={'id': self.shop.id}),
                                    {'name': 'New name', 'description': 'Test new description',
                                     'logo': 'def.png', 'theme': 'white'})

        updated_shop = Shop.objects.get(id=self.shop.id)
        self.assertRedirects(response, reverse('profile', kwargs={'id': self.user.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(updated_shop.name, 'New name')
        self.assertEqual(updated_shop.description, 'Test new description')

    def test_bad_update(self) -> None:
        self.client.login(username='myemail@gmail.com', password='123')

        response = self.client.post(reverse('shop_update', kwargs={'id': self.shop.id}),
                                    {'name': 'NEW NAME', 'description': 'Test new description', 'logo': 'def.png',
                                     'theme': 'green'})


        self.assertContains(response, 'Выберите корректный вариант. green нет среди допустимых значений.')
        self.assertEqual(response.status_code, 200)


class ShopDeleteCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email='myemail@gmail.com', phone='77014779047', password='123')
        self.shop = Shop.objects.create(user_id=self.user.id, name='New', description='Test description', theme='black')

    def test_delete_success(self) -> None:
        self.client.login(username='myemail@gmail.com', password='123')

        response = self.client.post(reverse('shop_delete', kwargs={"id": self.shop.id}))

        with self.assertRaises(ObjectDoesNotExist):
            Shop.objects.get(id=self.shop.id)
        self.assertFalse(Shop.objects.filter(id=self.shop.id).exists())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile', kwargs={'id': self.user.id}))

    def test_delete_false(self) -> None:
        self.client.login(username='myemail@gmail.com', password='123')

        response = self.client.post(reverse('shop_delete', kwargs={'id': self.shop.id+1}))

        self.assertTrue(Shop.objects.filter(id=self.shop.id))
        self.assertEqual(response.status_code, 404)


class ShopListCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email='myemail@gmail.com', phone='77014779047', password='123')
        self.shop = Shop.objects.create(user_id=self.user.id, name='New', description='Test description', theme='black')

    def test_success(self) -> None:
        client = Client()

        url = reverse('shop_view', kwargs={'shop_id': self.shop.id})

        response = client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertIn('shop', response.context)
        self.assertIn('products', response.context)
        self.assertIn('category_product', response.context)
        self.assertEqual(response.context['shop'], self.shop)

    def test_false(self) -> None:
        client = Client()

        url = reverse('shop_view', kwargs={'shop_id': self.shop.id + 1})

        response = client.get(url)

        self.assertEqual(response.status_code, 404)


class ProfileCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email='myemail@gmail.com', phone='77014779047', password='123')
        self.other_user = User.objects.create_user(email='bad@mail.ru', phone='77011919099', password='555')
        self.url = reverse('profile', kwargs={'id': self.user.id})

    def test_profile_success(self) -> None:
        self.client.login(username='myemail@gmail.com', password='123')

        response = self.client.get(self.url)

        self.assertIn('shops', response.context)
        self.assertEqual(response.status_code, 200)

    def test_fail_profile(self) -> None:
        self.client.login(username='bad@mail.ru', password='555')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)


class ProductCreateCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email='pr@gmail.com', password='123', phone='87014779047')
        self.shop = Shop.objects.create(user_id=self.user.id, name='New', description='Test description', theme='black')

    def test_product_create_success(self) -> None:
        self.client.login(username='pr@gmail.com', password='123')
        image_file = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('create_product', kwargs={"shop_id": self.shop.id}), {
            'shop': self.shop.id,
            'name': 'test product',
            'description': 'test test',
            'vendor_code': "111111",
            'quantity': 1111,
            'price': 10000,
            'image': [image_file],
            'new_category': 'Test category'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Product.objects.filter(name='test product').exists())
        self.assertEqual(Product.objects.get(name='test product').shop, self.shop)

    def test_fail_create_product(self):
        self.client.login(username='pr@gmail.com', password='123')
        image_file = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('create_product', kwargs={"shop_id": self.shop.id}), {
            'shop': self.shop.id,
            # 'name': 'test product',
            'description': 'test test',
            'vendor_code': "111111",
            'quantity': 1111,
            'price': 10000,
            'image': [image_file],
            'new_category': 'Test category'
        }, follow=True)


        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Обязательное поле.')


class ProductDetailCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email='pr@gmail.com', password='123', phone='87014779047')
        self.shop = Shop.objects.create(user_id=self.user.id, name='New', description='Test description', theme='black')
        self.product = Product.objects.create(shop=self.shop, name='TEST', description='Test test',
                                              vendor_code='44321', quantity=10, price=1000,)

    def test_success_detail(self) -> None:
        self.client.login(email='pr@gmail.com', password='123')
        url = reverse('detail_product', kwargs={'id': self.product.id})
        response = self.client.get(url)

        self.assertIn('now', response.context)
        self.assertIn('shop', response.context)
        self.assertIn('attributes', response.context)
        self.assertEqual(response.status_code, 200)

    def test_fail_detail(self) -> None:
        self.client.login(username='pr@gmail.com', password='123')
        url = reverse('detail_product', kwargs={'id': self.product.id + 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class ProductDeleteCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email='pr@gmail.com', password='123', phone='87014779047')
        self.shop = Shop.objects.create(user_id=self.user.id, name='New', description='Test description', theme='black')
        self.product = Product.objects.create(shop=self.shop, name='TEST', description='Test test',
                                              vendor_code='44321', quantity=10, price=1000, )

    def test_success_delete(self) -> None:
        self.client.login(username='pr@gmail.com', password='123')
        response = self.client.post(reverse('delete_product', kwargs={'id': self.product.id}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('shop_products', kwargs={'id': self.shop.id}))
        self.assertFalse(Product.objects.filter(name=self.product.name).exists())
        with self.assertRaises(ObjectDoesNotExist):
            Product.objects.get(name=self.product.name)

    def test_fail_delete(self) -> None:
        self.client.login(username='pr@gmail.com', password='123')
        response = self.client.post(reverse('delete_product', kwargs={'id': self.product.id + 1}))

        self.assertEqual(response.status_code, 404)

    def test_fail_no_auth(self) -> None:
        self.client.login(username='pr@gmail.commm', password='123')
        response = self.client.post(reverse('delete_product', kwargs={'id': self.product.id}))

        self.assertTrue(Product.objects.filter(id=self.product.id).exists())
        self.assertEqual(response.status_code, 302)


class ProductUpdateCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(email='pr@gmail.com', password='123', phone='87014779047')
        self.shop = Shop.objects.create(user_id=self.user.id, name='New', description='Test description', theme='black')
        self.product = Product.objects.create(shop=self.shop, name='TEST', description='Test test',
                                              vendor_code='44321', quantity=10, price=1000, )

    def test_success_update(self) -> None:
        self.client.login(username='pr@gmail.com', password='123')

        response = self.client.post(reverse('edit_product', kwargs={'id': self.product.id}), {
            'name': 'Update',
            'description': 'test test',
            'vendor_code': "111111",
            'quantity': 1111,
            'price': 10000,
            'new_category': 'Test category'
        }, follow=True)

        updated_product = Product.objects.get(name='Update')
        self.assertEqual(updated_product.name, 'Update')
        self.assertEqual(response.status_code, 200)


