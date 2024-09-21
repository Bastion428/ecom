from django import template

register = template.Library()


@register.filter(name="key")
def key(dict, key):
    key = str(key)
    return dict[key]
