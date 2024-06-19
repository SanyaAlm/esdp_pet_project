from _decimal import Decimal

from django import template

register = template.Library()


@register.simple_tag(name='divide')
def divide(value, divisor):
    try:
        result = Decimal(value) / Decimal(divisor)
        return round(result, 2)
    except (ValueError, ZeroDivisionError):
        return None
