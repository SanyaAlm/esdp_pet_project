import decimal

from shop.models import TimeDiscount


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def get_discount(item) -> None:
    product = item.product
    quantity = decimal.Decimal(item.quantity)
    item.unit_price = product.price * quantity

    if discount := product.discounted_price:
        item.unit_price = discount * quantity

    if TimeDiscount.objects.filter(product=product).exists():
        time_discount = TimeDiscount.objects.get(product=product)
        item.unit_price = time_discount.discounted_price * quantity
    item.save()
