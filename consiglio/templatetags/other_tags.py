from django.template import Library
from django.utils.numberformat import format

register = Library()

@register.filter
def floatdot(value, decimal_pos=4):
    return format(value, ".", decimal_pos)

floatdot.is_safe = True