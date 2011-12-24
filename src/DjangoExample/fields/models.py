# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.db.models import Model, ForeignKey, Q, \
  BooleanField, CharField, IntegerField
from django.utils.translation import ugettext_lazy as _
from DjangoExample.forms import modelField
from DjangoExample.i18n import I18n
from DjangoExample.validators import LatinCharsValidator

BooleanField = modelField(BooleanField)
CharField = modelField(CharField)
IntegerField = modelField(IntegerField)

# #####################################################################
# Базовая модель динамического поля
# #####################################################################

@I18n('name')
class Field(Model):

  target = CharField(_('Target Table'),
    max_length=20,
    blank=False,
    choices=(
      ('company', _('Company')),
      ('contact', _('Contact'))
    ),
    default='company')

  fieldType = CharField(_('Field Type'),
    max_length=20,
    blank=False,
    choices=(
      ('text',     _('Text')),
      ('date',     _('Date')),
      ('list',     _('Choice from list')),
      ('ministry', _('Ministry')),
      ('sector',   _('Sector')),
    ),
    default='text')

  name = CharField(_('Field Name'),
    max_length=128,
    blank=False)

  bookmarkName = CharField(_('Bookmark Name'),
    max_length=128,
    blank=False,
    unique=True,
    validators=[LatinCharsValidator()])

  fieldName = CharField(_('Field Name'),
    max_length=128,
    blank=True,
    validators=[LatinCharsValidator()])

  required = BooleanField(_('Required'),
    default=False)

  # дополнительные настройки для тестовых полей
  minLength = IntegerField(_('Minumum Length'), blank=True)
  maxLength = IntegerField(_('Maximum Length'), blank=True)

  class Meta:
    verbose_name = _('Field')
    verbose_name_plural = _('Fields')

  # ===================================================================
  # Методы "бизнес-логики" и не очень
  # ===================================================================

  def getFieldName(self):
    return self.fieldName if self.fieldName else self.bookmarkName

  def isSystem(self):
    return bool(self.fieldName)

  # ===================================================================
  # Дополнительный метод валидации validateUniqueBookmarkName()
  # ===================================================================

  FIELDS_REQUIRED_TO_VALIDATE_UNIQUE_BOOKMARK_NAME = ( 'target', 'bookmarkName', 'fieldName' )

  def needValidateUniqueBookmarkName(self, errors):
    #
    # ValidateUniqueBookmarkName не надо вызывать, когда хотя бы одно из полей,
    # по которым проверяется уникальность, уже помечено как невалидное.  Если
    # этого не делать, пользователь получит лишние ошибки валидации, а нас
    # придётся бороться с ошибками "Can not use None as query value" внутри
    # validateUniqueBookmarkName().
    #
    for fieldName in errors:
      if fieldName in self.FIELDS_REQUIRED_TO_VALIDATE_UNIQUE_BOOKMARK_NAME:
        return False
    return True

  def validateUniqueBookmarkName(self):
    '''
    Дополнительный метод валидации, проверяющий уникальность (target, ISNULL(fieldName, bookmarkName)).
    Автоматически вызывается в методе full_clean() модели, но, так как этот метод не используется
    при сохранении из форм, привязанных к модели, в таких формах метод необходимо вызывать вручную,
    предварительно вызвав needValidateUniqueBookmarkName().
    '''

    fieldName = self.getFieldName()
    qs = Field.objects.filter(
      Q(target__exact=self.target),
      Q(fieldName__iexact=fieldName) |
      Q(fieldName__isnull=True, bookmarkName__iexact=fieldName))

    # Exclude the current object from the query if we are editing an
    # instance (as opposed to creating a new one)
    if not self._state.adding and self.pk is not None:
        qs = qs.exclude(pk=self.pk)

    if qs.exists():
      message = self.unique_error_message(Field, ('bookmarkName',))
      raise ValidationError({ 'bookmarkName': [message] })

  # ===================================================================
  # Переопределение стандартных методов модели
  # ===================================================================

  def validate_unique(self, exclude=None):
    errors = {}
    try:
      Model.validate_unique(self, exclude)
    except ValidationError as e:
      errors = e.update_error_dict(errors)

    # вызываем дополнительный метод валидации validateUniqueBookmarkName()
    if self.needValidateUniqueBookmarkName(errors):
      try:
        self.validateUniqueBookmarkName()
      except ValidationError as e:
        errors = e.update_error_dict(errors)

    if errors:
      raise ValidationError(errors)

# #####################################################################
# Модель опции динамического поля типа "Список"
# #####################################################################

@I18n('name')
class FieldOption(Model):
  field = ForeignKey(Field,
    verbose_name=_('Field'),
    db_column='field')
  name = CharField(
    name=_('Name'),
    max_length=128)
  bookmarkName = CharField(
    name=_('Bookmark Name'),
    max_length=128,
    validators=[LatinCharsValidator()])

  class Meta:
    verbose_name = _('Field Option')
    verbose_name_plural = _('Field Options')
    unique_together=(('field', 'bookmarkName'),)
