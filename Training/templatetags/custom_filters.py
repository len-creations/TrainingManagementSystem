from django import template
import random
register = template.Library()

@register.filter
def range_filter(value):
    return range(value)

@register.filter
def random_color(_):
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))