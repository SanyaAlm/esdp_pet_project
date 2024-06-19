import datetime
import decimal

import random
import redis
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView

from .serializers import TimeDiscountSerializer, BucketSerializer, ProductSerializer
from accounts.models import Account, User
from shop.models import TimeDiscount, Product, Bucket, Order, OrderProducts, Shop
from shop.views import get_client_ip
from django.http import HttpResponse
from shop.views.additional_functions import get_discount
from django.forms.models import model_to_dict
from .serializers import TimeDiscountSerializer, BucketSerializer, ProductSerializer, OrderSerializer, OrderIdSerializer, ProductXMLSerializer, ShopTgSerializer
import requests


class LogoutView(APIView):

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            user.auth_token.delete()
        return JsonResponse({
            'status': 200
        })


class TimeDiscountViewSet(viewsets.ModelViewSet):
    queryset = TimeDiscount.objects.all()
    serializer_class = TimeDiscountSerializer
    lookup_url_kwarg = 'id'
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):
        serializer = TimeDiscountSerializer(data=request.data)

        if serializer.is_valid():
            time_discount = serializer.save()
            product = time_discount.product
            price = product.price

            if time_discount.discount:
                discounted_price = float(price) - (
                        float(price) * (float(time_discount.discount) / 100))

            elif time_discount.discount_in_currency:
                discounted_price = price - time_discount.discount_in_currency

            else:
                discounted_price = 0

            time_discount.discounted_price = discounted_price
            time_discount.save()

            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except TimeDiscount.DoesNotExist:
            return Response({'error': 'Not found'})

    @action(detail=False, methods=['GET'], url_path='get-discount-by-product')
    def get_discount_by_product(self, request):
        product_id = request.query_params.get('product_id')

        try:
            discount = TimeDiscount.objects.get(product_id=product_id)

            return Response({'discount_id': discount.id})
        except TimeDiscount.DoesNotExist:
            return Response({'error': 'Discount not found for the product'})

    @action(detail=True, methods=['get'], url_path='check-start')
    def check_start(self, request, id=None):
        discount = self.get_object()

        start_date = discount.start_date.astimezone(timezone.get_current_timezone())
        now = timezone.now()

        if now >= start_date:
            return Response({'started': True})

        else:
            return Response({'started': False})


class BucketViewSet(viewsets.ModelViewSet):
    queryset = Bucket.objects.all()
    serializer_class = BucketSerializer

    @action(detail=False, methods=['POST'])
    def add_to_cart(self, request, *args, **kwargs):
        shop_id = request.data.get('shop')
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)
        user = request.data.get("user")

        ip_address = get_client_ip(request)

        try:
            user = Account.objects.get(user_id=user)
            created = Bucket.objects.create(user=user, product_id=product_id, shop_id=shop_id,
                                            quantity=quantity)

        except Account.DoesNotExist:
            created = Bucket.objects.create(ip_address=ip_address, product_id=product_id, shop_id=shop_id,
                                            quantity=quantity)

        get_discount(created)
        product = Product.objects.get(id=product_id)
        product.quantity -= int(quantity)
        product.save()
        serializer = self.get_serializer(created)

        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['DELETE'])
    def remove_from_cart(self, request, *args, **kwargs):
        item_id = self.kwargs.get('pk')
        item = Bucket.objects.get(id=item_id)
        item.product.quantity += item.quantity
        item.product.save()

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]

        else:
            ip = request.META.get('REMOTE_ADDR')

        return ip

    @action(detail=True, methods=['DELETE'])
    def remove_from_cart(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    @action(detail=True, methods=['PUT'])
    def update_quantity(self, request, *args, **kwargs):
        try:
            item_id = self.kwargs.get('pk')
            new_quantity = int(request.data.get('new_quantity'))
            item = Bucket.objects.get(id=item_id)
            if new_quantity > item.product.quantity:
                return JsonResponse({'success': False, 'error': 'Not enough quantity in stock'}, status=status.HTTP_400_BAD_REQUEST)
            item.unit_price = (item.unit_price / item.quantity) * new_quantity
            item.product.quantity -= new_quantity - item.quantity
            item.quantity = new_quantity
            item.save()
            item.product.save()

            bucket_all = Bucket.objects.filter(Q(ip_address=item.ip_address)) or Bucket.objects.filter(
                Q(user_id=item.user))

            total_price = sum(item.unit_price for item in bucket_all)
            product_id = item.product.id

            return JsonResponse({'success': True, "total_price": total_price, 'product_id': product_id,
                                 'unit_price': item.unit_price}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'id'
    lookup_field = 'id'




class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['POST'])
    def create_order(self, request, *args, **kwargs):
        data = request.data
        shop = data.get('shop')
        total = data.get('total')
        order = Order.objects.create(shop_id=shop, total=total)

        products = Bucket.objects.filter(id__in=data.get('products').split(','))
        self.add_products(products, order)

        order.payer_city = data.get('payer_city')
        order.payer_address = data.get('payer_address')
        order.payer_phone = data.get('payer_phone')
        order.payer_email = data.get('payer_email')
        order.payer_surname = data.get('payer_surname')
        order.payer_name = data.get('payer_name')
        order.payer_postal_code = data.get('payer_postal_code')
        order.save()

        if account := data.get('account'):
            order.account = Account.objects.get(id=account)
            order.save()
            return JsonResponse(data={'order_id': order.id, 'user_id': account}, status=status.HTTP_201_CREATED)
        else:
            ip = get_client_ip(request)
            order.user_ip = ip
            order.save()

        return JsonResponse(data={'order_id': order.id}, status=status.HTTP_201_CREATED)
    @staticmethod
    def add_products(products, order):
        for item in products:
            OrderProducts.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_per_product=item.unit_price,
            )
            item.delete()


class CreateCheck(APIView):
    def get_api_token(self):
        url = settings.URL_REKASSA + 'auth/login'
        api_key = settings.TOKEN_REKASSA
        data = {
            "number": "BHUM2VQS-QA1",
            "password": "AzYKbddpL*5c2ocLaKK0hjBzaqz*AwAP"
        }
        try:
            response = requests.post(url, params={'apiKey': api_key}, json=data)
            response.raise_for_status()

            return response.text
        except requests.RequestException as e:
            raise ValueError(f"Error getting API token: {e}")

    def register_ticket(self, api_token, order_products):
        url = settings.URL_REKASSA + 'crs/1316/tickets'
        items = []
        total_bills = 0
        for op in order_products:
            product = op.product
            product_price = product.price if product.discount == 0 else product.discounted_price
            items.append({
                "type": "ITEM_TYPE_COMMODITY",
                "commodity": {
                    "name": product.name,
                    "sectionCode": str(product.category_id),
                    "quantity": op.quantity * 1000,
                    "price": {
                        "bills": str(product_price),
                        "coins": 0
                    },
                    "sum": {
                        "bills": str(op.quantity * product_price),
                        "coins": 0
                    },
                    "auxiliary": [
                        {
                            "key": "UNIT_TYPE",
                            "value": "PIECE"
                        }
                    ]
                }
            })
            total_bills += op.quantity * product_price
        payments = [
            {
                "type": "PAYMENT_CASH",
                "sum": {
                    "bills": str(total_bills),
                    "coins": 0
                }
            }
        ]

        now = datetime.datetime.now()
        data = {
            "operation": "OPERATION_SELL",
            "dateTime": {
                "date": {
                    "year": str(now.year),
                    "month": str(now.month).zfill(2),
                    "day": str(now.day).zfill(2)
                },
                "time": {
                    "hour": str(now.hour).zfill(2),
                    "minute": str(now.minute).zfill(2),
                    "second": str(now.second).zfill(2)
                }
            },
            "payments": payments,
            "items": items,
            "amounts": {
                "total": {
                    "bills": str(total_bills),
                    "coins": 0
                },
                "taken": {
                    "bills": str(total_bills),
                    "coins": 0
                },
                "change": {
                    "bills": "0",
                    "coins": 0
                }
            }
        }
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        print(data)
        try:
            response = requests.post(url, json=data, headers=headers)
            print(response)
            response.raise_for_status()

            return response.json().get('id')
        except requests.RequestException as e:
            raise ValueError(f"Error registering ticket: {e}")

    def download_receipt(self, api_token, ticket_id, payer_email):
        url = settings.URL_REKASSA + f"crs/1316/tickets/{ticket_id}/receipts"
        data = {
            'type': 'EMAIL',
            "receiver": {
                "email": f"{payer_email}"
            }
        }
        headers = {
            'Authorization': f'Bearer {api_token}'
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValueError(f"Error downloading receipt: {e}")

    def post(self, request, *args, **kwargs):
        serializer = OrderIdSerializer(data=request.data)
        try:
            if serializer.is_valid():
                order_id = serializer.validated_data.get('order_id')
                try:
                    order_products = OrderProducts.objects.filter(order_id=order_id)
                except Order.DoesNotExist:
                    return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)

                api_token = self.get_api_token()
                print(api_token)
                ticket_id = self.register_ticket(api_token, order_products)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            payer_email = serializer.validated_data.get('email')
            print(payer_email)
            # check
            receipt_data = self.download_receipt(api_token, ticket_id, payer_email)
            return Response(receipt_data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def product_list_xml(request, partner_id):

    shop = Shop.objects.get(partner_id=partner_id)
    products = Product.objects.filter(shop=shop.id)
    products_list = [model_to_dict(product, fields=['id', 'shop_id', 'price', 'quantity', 'name', 'vendor_code',]) for product in products]

    return JsonResponse(products_list, safe=False)


class TelegramShopsViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.filter(tg_token__isnull=False)
    serializer_class = ShopTgSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return JsonResponse({'shop': serializer.data}, safe=False)


def user_detail_api_view(request, id, *args, **kwargs):
    user = User.objects.get(id=id)

    code = random.randint(1000, 9999)
    data = {'id': user.id, 'phone': user.phone, 'code': code}

    redis_client = redis.StrictRedis(host='redis', port=6379, db=1)

    key = user.phone
    value = str(code)

    redis_client.set(key, value)
    redis_client.expire(key, 60)

    return JsonResponse(data=data, status=200)
