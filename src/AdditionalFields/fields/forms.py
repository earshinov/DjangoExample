# -*- coding: utf-8 -*-

from django.forms import ChoiceField, IntegerField
from django.utils.translation import ugettext, ugettext_lazy as _
from AdditionalFields.forms import formField
from AdditionalFields.forms import ModelForm
from fields.models import Field
from django.core.exceptions import ValidationError

ChoiceField = formField(ChoiceField)
IntegerField = formField(IntegerField)


class FieldForm(ModelForm):
  fieldType = ChoiceField(label=_('Field Type'), choices=(
    ('text',     _('Text')),
    ('date',     _('Date')),
    ('list',     _('Choice from list')),
    ('ministry', _('Ministry')),
    ('sector',   _('Sector')),
  ))

  # для текстовых полей
  minLength = IntegerField(label=_('Minimum Length'), required=False)
  maxLength = IntegerField(label=_('Maximum Length'), required=False)

  class Meta:
    model = Field
    exclude = ('fieldName',)

  FIELDS_THAT_CANNOT_BE_CHANGED_AFTER_CREATION = ( 'target', 'fieldType', 'bookmarkName' )

  def __init__(self, *args, **kw):
    super(FieldForm, self).__init__(*args, **kw)

    # отображаем поле fieldType после target
    fieldOrder = self.fields.keyOrder
    fieldOrder.pop(fieldOrder.index('fieldType'))
    fieldOrder.insert(fieldOrder.index('target') + 1, 'fieldType')

    # добавляем подсказки
    message = ugettext('Cannot be changed afterwards')
    for fieldName in self.FIELDS_THAT_CANNOT_BE_CHANGED_AFTER_CREATION:
      self.fields[fieldName].notes.append(message)

  def full_clean(self):
    super(FieldForm, self).full_clean()

    # в этом случае никакая валидация проводиться не должна
    if not self.is_bound:
      return

    # вызываем для модели дополнительный метод валидации
    # Field.validateUniqueBookmarkName
    if self.instance.needValidateUniqueBookmarkName(self._errors):
      try:
        self.instance.validateUniqueBookmarkName()
      except ValidationError as e:
        self._errors = e.update_error_dict(self._errors)
