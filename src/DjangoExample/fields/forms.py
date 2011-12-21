# -*- coding: utf-8 -*-

from django.forms import ChoiceField, IntegerField
from django.utils.translation import ugettext
from DjangoExample.forms import formField
from DjangoExample.forms import ModelForm
from fields.models import Field
from django.core.exceptions import ValidationError

ChoiceField = formField(ChoiceField)
IntegerField = formField(IntegerField)


class FieldForm(ModelForm):

  class Meta:
    model = Field
    exclude = ('fieldName',)

  FIELDS_THAT_CANNOT_BE_CHANGED_AFTER_CREATION = ( 'target', 'fieldType', 'bookmarkName' )

  def __init__(self, *args, **kw):
    super(FieldForm, self).__init__(*args, **kw)

    # добавляем подсказки
    message = ugettext('Cannot be changed afterwards')
    for fieldName in self.FIELDS_THAT_CANNOT_BE_CHANGED_AFTER_CREATION:
      self.fields[fieldName].notes.append(message)

    # Если редактируется существующее поле, отключаем контролы,
    # недействительные для данного типа поля.
    if self.instance and self.instance.id:
      if self.instance.fieldType != 'text':
        del self.fields['minLength']
        del self.fields['maxLength']

    # если редактируется существующее поле, делаем серенькими контролы,
    # значения которых нельзя изменить
    if self.instance and self.instance.id:
      for fieldName in self.FIELDS_THAT_CANNOT_BE_CHANGED_AFTER_CREATION:
        self.fields[fieldName].widget.attrs['readonly'] = True

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


  def clean_target(self):
    # Запрещаем изменение этого поля, когда запись в базе уже создана
    #
    # <http://stackoverflow.com/questions/324477/>
    # In a django form, How to make a field readonly (or disabled) so that it cannot be edited?
    #
    if self.instance and self.instance.id:
      # оставляем значение неизменным
      return self.instance.target
    else:
      # используем значение, уже проставленное фреймворком из параметров запроса
      return self.cleaned_data['target']

  def clean_fieldType(self):
    # Запрещаем изменение этого поля, когда запись в базе уже создана.
    # Полная аналогия с target.
    if self.instance and self.instance.id:
      # оставляем значение неизменным
      return self.instance.fieldType
    else:
      # используем значение, уже проставленное фреймворком из параметров запроса
      return self.cleaned_data['fieldType']

  def clean_bookmarkName(self):
    # Запрещаем изменение этого поля, когда запись в базе уже создана.
    # Полная аналогия с target.
    if self.instance and self.instance.id:
      # оставляем значение неизменным
      return self.instance.bookmarkName
    else:
      # используем значение, уже проставленное фреймворком из параметров запроса
      return self.cleaned_data['bookmarkName']


  def clean_minLength(self):
    #
    # При добавлении нового динамического поля не вставляем
    # minLength, если поле не текстовое.
    #
    # NOTE 1: Не обрабатываем здесь случай редактирования
    # существующего не-текстового поля, потому что тогда
    # поле minLength просто не будет выведено в форме
    #
    # NOTE 2: Это действие не является строго обязательным —
    # нет ничего страшного в том, что запищем minLength.
    # Можно рассматривать этот код как демонстрацию.
    #
    # <http://stackoverflow.com/questions/3207036/>
    # Django: Can I restrict which fields are saved back to the database using forms?
    #

    # Опираемся здесь на то, что fieldType в списке полей идёт до minLength,
    # поэтому к моменту вызова этого кода будет уже записан из запроса.
    if self.cleaned_data['fieldType'] != 'text':
      # записываем в базу NULL
      return None
    else:
      # используем значение, уже проставленное фреймворком из параметров запроса
      return self.cleaned_data['minLength']

  def clean_maxLength(self):
    # При добавлении нового динамического поля не вставляем maxLength,
    # если поле не текстовое.  Полная аналогия с minLength выше.
    if self.cleaned_data['fieldType'] != 'text':
      # записываем в базу NULL
      return None
    else:
      # используем значение, уже проставленное фреймворком из параметров запроса
      return self.cleaned_data['maxLength']
