# -*- coding: utf-8 -*-
# http://stackoverflow.com/questions/1809874/

from django import template
register = template.Library()

@register.filter()
def field_widget_type(field):
  return field.field.widget.__class__.__name__
