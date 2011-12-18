# -*- coding: utf-8 -*-

from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


class AnnotatedValidator(object):
  '''
  Маркерный интерфейс, говорящий нашим переопределённым классам полей,
  что при добавлении к полю такого валидатора его сообщение валидации
  должно добавляться в качестве примечания (note) к полю.
  '''
  pass


class LatinCharsValidator(RegexValidator, AnnotatedValidator):
  def __init__(self):
    RegexValidator.__init__(self, '[a-zA-Z]+', _('Only latin characters'))
