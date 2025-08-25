# users/templatetags/template_extras.py
from django import template

register = template.Library()

@register.filter(name='attr')
def attr(field, css):
    attrs = {}
    definition = css.split(',')

    for d in definition:
        if ':' in d:
            key, val = d.split(':')
            attrs[key.strip()] = val.strip()

    return field.as_widget(attrs=attrs)