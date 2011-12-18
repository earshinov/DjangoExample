# -*- coding: utf-8 -*-

from django.conf import settings
from easymode.i18n.decorators import I18n as easymodeI18n
from easymode.i18n.meta.utils import get_field_from_model_by_name
from easymode.utils.languagecode import get_all_language_codes, get_real_fieldname


getLocalizedFieldName = get_real_fieldname

def getLocalizedFieldNames(fieldName):
  for code, unused_name in settings.LANGUAGES:
    yield getLocalizedFieldName(fieldName, code)


class I18n(object):
  '''
  Замена для easymode.i18n.decorators.I18n, которая не сбрасывает
  локализованным полям флаг blank (т.е. не делает эти поля
  опциональными для заполнения)
  '''
  def __init__(self, *localizedFields, **kw):
    self.localizedFields = localizedFields
    self.decorated = easymodeI18n(*localizedFields)
    self.makeLocalizedFieldsOptional = kw.get('makeLocalizedFieldsOptional', False)

  def __call__(self, cls):
    if not self.makeLocalizedFieldsOptional:
      blankFlags = self.__collectBlank(cls)
    cls = self.decorated(cls)
    if not self.makeLocalizedFieldsOptional:
      self.__restoreBlank(cls, blankFlags)
    return cls

  def __collectBlank(self, cls):
    blankFlags = []
    for field in self.localizedFields:
      attr = get_field_from_model_by_name(cls, field)
      blankFlags.append(attr.blank)
    return blankFlags

  def __restoreBlank(self, cls, blankFlags):
    for field, blank in zip(self.localizedFields, blankFlags):
      for code in get_all_language_codes():
        i18n_attr = get_field_from_model_by_name(cls, getLocalizedFieldName(field, code))
        i18n_attr.blank = blank
