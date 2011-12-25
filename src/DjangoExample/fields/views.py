# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.template import RequestContext

from fields.models import Field, FieldOption
from fields.forms import FieldForm
from DjangoExample.forms import ModelForm
from DjangoExample.HeaderFooter import HeaderFooter


def fieldList(request):
  return render_to_response('field-list.html',
    {
      'fields': Field.objects.all(),
      'header_footer': HeaderFooter('fields'),
    },
    context_instance=RequestContext(request))


class FieldFormAndFormset(object):

  def __init__(self, request=None, instance=None):
    field = instance # alias
    post = None if not request else request.POST

    self.form = FieldForm(post, instance=field)
    self.optionsFormset = None

    # Создание формсета, если необходимо
    if not field or (field and field.fieldType == 'list'):
      # Используем form=<наш базовый класс формы>!
      OptionsFormset = inlineformset_factory(Field, FieldOption, form=ModelForm)
      #
      # Передаём instance=form.instance, а не field.  В качестве field мог
      # быть передан None; в этом случае пустой instance создаётся внутри
      # конструктора формы.
      #
      # При выполнении сохранения формсет пунктов списка будет обращаться к
      # заданному instance за идентификатором динамического поля.  В случае,
      # когда на странице добавляется новое динамическое поле (а не редактируется
      # существующее), особо важно, чтобы instance, на который ссылаются форма
      # и формсет, был одним объектом, чтобы формсет узнал идентификатор
      # вновь добавленной записи.
      #
      self.optionsFormset = OptionsFormset(post, instance=self.form.instance)

  def is_valid(self):
    return self.form.is_valid() and (not self.optionsFormset or self.optionsFormset.is_valid())

  def save(self):
    self.form.save()
    if self.form.instance.fieldType == 'list':
      #
      # Здесь проверка не на существование self.optionsFormset, потому что при
      # заведении нового динамического поля формсет показывается, но должен быть
      # сохранён, только если созданное динамическое поле имеет тип «выбор из списка»
      #
      # Дополнительно существование optionsFormset проверять не надо. Для
      # существующего динамического поля формсет создаётся тогда и только тогда, когда
      # это динамическое поле имеет тип «выбор из файла», а тип динамического поля
      # нельзя поменять после создания.
      #
      self.optionsFormset.save()


def fieldEditor(request):
  # Можно передавать идентификатор редактируемой записи не через параметр
  # URL (field-editor?id={id}), а непосредственно в URL (fields/edit/{id}/).
  # С точки зрения реализации это абсолютно непринципиально: оба варианта
  # реализуются с одинаковой лёгкостью.  Возможно, второй вариант более
  # правилен идеологически.

  field = None
  instanceId = request.REQUEST.get('id')
  if instanceId:
    field = get_object_or_404(Field, pk=instanceId)

  backurl = request.REQUEST.get('backurl')

  x = None
  if request.method == 'POST':
    if field and 'delete' in request.POST:
      field.delete()
      if backurl:
        return HttpResponseRedirect(backurl)
      return HttpResponseRedirect(reverse(fieldEditor))
    else:
      x = FieldFormAndFormset(request, instance=field)
      if 'save' in request.POST:
        with transaction.commit_on_success():
          if x.is_valid():
            savedField = x.save()
            if backurl:
              return HttpResponseRedirect(backurl)
            if not field: # was inserted
              return HttpResponseRedirect(reverse(fieldEditor) + u'?id=' + unicode(savedField.id))

  if x is None:
    x = FieldFormAndFormset(instance=field)

  if field is not None:
    x.form.addHidden('id', field.id)
  if backurl:
    x.form.addHidden('backurl', backurl)

  return render_to_response('field-editor.html', {
    'form': x.form,
    'optionsFormset': x.optionsFormset,
    'header_footer': HeaderFooter('fields'),
  })

