# -*- coding: utf-8 -*-
# Основано на <http://djangosnippets.org/snippets/539/>

from django import template


class AssignValue(template.Node):

  def __init__(self, name, value):
    self.name = name
    self.value = value

  def render(self, context):
    context[self.name] = self.value.resolve(context, True)
    return ''


class AssignChunk(template.Node):

  def __init__(self, name, nodelist):
    self.name = name
    self.nodelist = nodelist

  def render(self, context):
    context[self.name] = self.nodelist.render(context)
    return ''


def assign(parser, token):
    '''
    Присвоение чего-либо переменной в текущем контексте.

    Пример 1 (присвоение другой переменной)::

      {% assign list entry.get_related %}
      {{ list }}

    Пример 2 (присвоение отрендеренного куска HTML)::

      {% assign title %}
        {% if instance %}
          {{ instance.name }}
        {% else %}
          None
        {% endif %}
      {% endassign %}
    '''
    bits = token.split_contents()
    if len(bits) == 2:
      nodelist = parser.parse(('endassign',))
      parser.delete_first_token()
      # присвоение переменной отрендеренного куска HTML, вложенного в блок {% assign %} ... {% endassign %}
      return AssignChunk(bits[1], nodelist)
    elif len(bits) == 3:
      value = parser.compile_filter(bits[2])
      # присвоение переменной некоторого значения (ничего не рендерится)
      return AssignValue(bits[1], value)
    else:
      raise template.TemplateSyntaxError("'%s' tag takes one or two arguments" % bits[0])


register = template.Library()
register.tag('assign', assign)
