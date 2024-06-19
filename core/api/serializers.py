
from rest_framework import serializers
from shop.models import TimeDiscount, Product, Bucket, Order, Shop, Images, Category
from accounts.models import User
from django.utils import timezone
import xml.etree.ElementTree as ET


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['image']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['name', 'description', 'vendor_code', 'quantity', 'price', 'images', 'discounted_price', 'category']


class ShopTgSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Shop
        fields = ['id', 'name', 'description', 'logo', 'tg_token', 'products', ]
        read_only_fields = ['id', 'name', 'description', 'logo', 'tg_token', 'products']


class TimeDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeDiscount
        fields = '__all__'

    start_date = serializers.DateTimeField(
        required=True,
        error_messages={
            'required': 'Поле "Начало скидки" обязательно для заполнения.',
            'invalid': 'Введите корректные данные в поле "Начало скидки"'
        }
    )

    end_date = serializers.DateTimeField(
        required=True,
        error_messages={
            'required': 'Поле "Конец скидки" обязательно для заполнения.',
            'invalid': 'Введите корректные данные в поле "Конец скидки"'
        }
    )

    discount = serializers.IntegerField(
        required=False,
        error_messages={
            'invalid': 'Введите корректные данные в поле "Скидка в процентах"'
        }
    )

    discount_in_currency = serializers.IntegerField(
        required=False,
        error_messages={
            'invalid': 'Введите корректные данные в поле "Скидка в денежном эквиваленте"'
        }
    )

    discounted_price = serializers.IntegerField(required=False)

    def validate_start_date(self, value):
        current_datetime = timezone.now()
        current_datetime_without = current_datetime.replace(microsecond=0, second=0)

        if current_datetime_without > value:
            raise serializers.ValidationError("Дата и время начала скидки должна быть в будущем или настоящем ")

        return value

    def validate_end_date(self, value):
        current_datetime = timezone.now()

        if value <= current_datetime:
            raise serializers.ValidationError("Дата и время окончания скидки должна быть в будущем.")

        return value

    def validate_discount(self, value):
        if value < 1 or value > 99:
            raise serializers.ValidationError("Скидка должна быть в диапазоне от 1 до 99.")

        return value

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        discount = data.get('discount')
        discount_in_currency = data.get('discount_in_currency')
        product = data.get('product')

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("Дата и время начала должна быть меньше даты и времени окончания.")

        if not discount and not discount_in_currency:
            raise serializers.ValidationError(
                "Должно быть заполнено хотя бы одно из полей: 'Скидка в процентах' или 'Скидка в денежном эквиваленте'."
            )

        if discount and discount_in_currency:
            raise serializers.ValidationError(
                "Заполнено оба поля: 'Скидка в процентах' и 'Скидка в денежном эквиваленте', "
                "оставьте только одно поле заполненным."
            )

        if discount_in_currency:
            if product.price <= discount_in_currency:
                raise serializers.ValidationError("Скидка не может быть больше или равна цене продукта")

        return data


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderIdSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    email = serializers.EmailField()


class BucketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bucket
        fields = ["id", 'shop', 'product', 'quantity', 'ip_address', 'user']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["account", "user_ip", "shop", "products", "total", "date", "payer_name", "payer_surname", "payer_phone",
                  "payer_email", "payer_city", "payer_address", "payer_postal_code"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone']


class ProductXMLSerializer(serializers.ModelSerializer):
    @staticmethod
    def to_xml(products):

        root = ET.Element('kaspi_catalog', date='string', xmlns='kaspiShopping',)
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:schemaLocation', 'kaspiShopping http://kaspi.kz/kaspishopping.xsd')

        company = ET.SubElement(root, 'company')

        merchantid = ET.SubElement(company, 'merchantid')

        offers = ET.SubElement(company, 'offers')

        for product in products:

            merchantid.text = str(product.shop.id)
            company.text = product.shop.name
            offer = ET.SubElement(offers, 'offer', sku=str(product.id))

            model = ET.SubElement(offer, 'model')
            model.text = product.name
            availabilities = ET.SubElement(offer, 'availabilities')

            if product.quantity > 0:
                available = 'yes'
            else:
                available = 'no'

            availability = ET.SubElement(availabilities, 'availability', available=available, storeID=str(product.shop_id))

            price = ET.SubElement(offer, 'price')
            price.text = str(product.price)

        xml_data = ET.tostring(root, encoding='utf-8').decode()
        return xml_data

