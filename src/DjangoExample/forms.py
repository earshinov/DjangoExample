# -*- coding: utf-8 -*-

from copy import deepcopy, copy
from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.forms import BoundField as _BoundField
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from validators import AnnotatedValidator

# Примечания о реализации некоторых пунктов программы:
#
# 1. Django поддерживает отдельные списки валидаторов для поля модели и
#    полученного из этого поля поля ModelForm.  Поэтому для полей моделей и
#    форм приходится дублировать код, отвечающий за (1) добавление сообщений
#    валидации Annotated-валидаторов в список примечаний к полю; (2) удаление
#    этих примечаний при срабатывании Annotated-валидаторов (возвращении ими
#    ошибок валидации)
#
#    (1) для полей моделей: modelField$Proxy.__init__
#        для полей форм:    _FormFieldDecorator.__init__
#    (2) для полей моделей: ModelForm._post_clean
#        для полей форм:    _FormFieldDecorator.run_validators
#
#    Реализацию (2) для полей моделей необходимо проводить в ModelForm, а не в
#    поле модели, потому что примечания необходимо удалять не из полей модели,
#    а из полученных из них полей форм, к которым из полей модели просто так
#    обратиться не получится.

# #####################################################################
# Обёртки для полей моделей и форм
# #####################################################################

def modelField(fieldClass):
  '''
  Изменение поведения и расширение возможностей стандартных классов
  полей моделей. Использование:
  
    from django.db.models import CharField
    CharField = modelField(CharField)
    # и использовать как обычный CharField
  
  Перечень изменений и усовершенствований:
  
    1. Значение по умолчанию параметра null делается True (мне кажется, на уровне
       базы пустые строки почти всегда логично представлять как NULL)
    2. В конструктор добавляется keyword-аргумент notes для задания списка
       примечаний для поля (по умолчанию []).
    3. В список примечаний автоматически добавляются сообщения валидации
       переданных в конструктор Annotated-валидаторов
       
  Список примечаний хранится в поле экземпляра класса notes.
  
  Переопределяется метод formfield, так что при наличии модели Model и связанной с
  этой моделью формы ModelForm для полей модели, созданных с использованием
  modelField, в форме будут созданы поля, обёрнутые в formField. 
  '''
  class Proxy(fieldClass):

    def __init__(self, *args, **kw):
      
      if fieldClass is not models.BooleanField:
        # BooleanField не принимает null
        kw.setdefault('null', True)
      self.notes = kw.pop('notes', [])
      fieldClass.__init__(self, *args, **kw)
      self.notes.extend(_getValidatorNotes(self.validators))

    # Протаскивание обёртки над полем формы
    def formfield(self, *args, **kw):
      return _FormFieldDecorator(fieldClass.formfield(self, *args, **kw), self.notes[:])

  return Proxy


def formField(fieldClass):
  '''
  Изменение поведения и расширение возможностей стандартных классов
  полей форм.  Использование:
  
    from django.forms import CharField
    CharField = formField(CharField)
    # и использовать как обычный CharField
    
  Перечень изменений и усовершенствований:
  
    1. В конструктор добавляется keyword-аргумент notes для задания списка
       примечаний для поля (по умолчанию []).
    2. В список примечаний автоматически добавляются сообщения валидации
       переданных в конструктор Annotated-валидаторов
       
  Список примечаний хранится в поле экземпляра класса notes.
  '''
  def factory(*args, **kw):
    notes = kw.pop('notes', [])
    return _FormFieldDecorator(fieldClass(*args, **kw), notes)
  return factory


# Реализация паттерна Декоратор для поля формы в стиле Python.  Для полей формы
# недостаточно простого прокси в виде унаследованного класса, как в обёртке полей
# модели (modelField), так как такой прокси не получится навесить в переопределённом
# в modelField методе formfield().
#
# В список базовых классов добавляем "маркерный" forms.Field, по которому
# Django определяет, является ли поле класса формы полем формы или нет.
# На самом деле этот базовый класс даже не инициализируется.
#
class _FormFieldDecorator(forms.Field, object):
  
  def __init__(self, obj, notes):
    object.__init__(self)
    self.obj = obj
    self.notes = notes
    self.notes.extend(_getValidatorNotes(self.obj.validators))
    
  def __getattribute__(self, name):
    if name.startswith('__') and name.endswith('__') or name in ('obj', 'notes', 'run_validators'):
      return object.__getattribute__(self, name)
    else:
      return getattr(self.obj, name)
    
  def __deepcopy__(self, memo):
    #
    # Опытным путём выяснилось, что коллекция fields конкретной формы
    # формируется применением deepcopy к соответствующим полям класса формы,
    # и что в классе django.forms.Field __deepcopy__ переопределён, так чтобы
    # копировать только ограниченный набор атрибутов.  Здесь необходимо
    # расширить __deepcopy__, чтобы копировать и коллекцию notes. 
    #
    newone = copy(self)
    newone.obj = deepcopy(self.obj, memo)
    newone.notes = self.notes[:]
    memo[id(self)] = newone
    return newone
  
  def run_validators(self):
    # Удаление примечаний, соответствующих сообщениям валидации
    # сработавших (возвративших ошибку) Annotated-валидаторов.  Проверяем
    # просто по совпадению примечания и сообщения валидации. 
    try:
      self.obj.run_validators()
    except ValidationError as e:
      self.notes = [note for note in self.notes if note not in e.messages]
      raise


def _getValidatorNotes(validators):
  # Получить сообщения Annotated-валидаторов из переданного списка валидаторов
  for v in validators:
    if isinstance(v, AnnotatedValidator):
      yield v.message
      
# #####################################################################
# Обёртки для форм (пока только для используемой нами ModelForm)
# #####################################################################

class ModelForm(forms.ModelForm):
  
  # Проставление классу формы атрибута required_css_class, благодаря
  # чему для обязательных полей в вёрстку попадает заданный CSS-класс 
  required_css_class = 'required'

  # Протаскивание нашего расширенного класса BoundField вместо
  # стандартного BoundField для использования в шаблонах
  def __iter__(self):
    for name, field in self.fields.iteritems():
      yield BoundField(self, field, name)

  def addHidden(self, name, value):
    '''Добавление в форму скрытого поля'''
    field = HiddenField(initial=value)
    self.fields[name] = field
    return field
  
  def _post_clean(self):
    # Удаление примечаний, соответствующих сообщениям валидации
    # сработавших (возвративших ошибку) Annotated-валидаторов.  Проверяем
    # просто по совпадению примечания и сообщения валидации.
    super(ModelForm, self)._post_clean()
    for fieldName, field in self.fields.iteritems():
      if hasattr(field, 'notes') and fieldName in self._errors:
        field.notes = [note for note in field.notes if note not in self._errors[fieldName]]

class BoundField(_BoundField):

  def label_tag_with_suffix(self):
    '''
    Новый метод, дополняющий стандартный label_tag, для получения
    названия поля с завершающим двоеточием
    '''
    #
    # Возможно, этим методом лучше *заменить* label_tag, но тогда ситуации,
    # когда завершающая пунктуация не нужна, придётся отслеживать не на
    # уровне шаблона (см. form-template.html), а на уровне кода.  К таким
    # ситуациям относится случай, когда поле - чекбокс.
    #
    label = self.label
    if self.form.label_suffix and label[-1] not in ':?.!':
      label += self.form.label_suffix
    return self.label_tag(conditional_escape(label))

  def notes(self):
    '''Метод для получения списка примечаний поля в формате errorlist'''
    notes = self.field.notes
    if not notes:
      return u''
    li = ''.join(u'<li>%s</li>' % (note,) for note in notes)
    ul = u'<ul class="notelist">%s</ul>' % (li,)
    return mark_safe(ul)

class HiddenField(forms.CharField):

  def __init__(self, **kw):
    kw.setdefault('widget', forms.widgets.HiddenInput())
    forms.CharField.__init__(self, **kw)
