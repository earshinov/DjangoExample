# -*- coding: utf-8 -*-

from django import template
register = template.Library()

@register.filter()
def field_is_readonly(field):
  return field.field.widget.attrs["readonly"]
