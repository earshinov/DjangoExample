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

  form = None
  optionsFormset = None
  if request.method == 'POST':
    if field and 'delete' in request.POST:
      field.delete()
      if backurl:
        return HttpResponseRedirect(backurl)
      return HttpResponseRedirect(reverse(fieldEditor))
    else:

      form = FieldForm(request.POST, instance=field)
      if not field or (field and field.fieldType == 'list'):
        optionsFormset = inlineformset_factory(Field, FieldOption, form=ModelForm)(request.POST, instance=form.instance)
      if 'save' in request.POST:
        with transaction.commit_on_success():
          if form.is_valid() and (not optionsFormset or optionsFormset.is_valid()):
            form.save()
            if form.instance.fieldType == 'list':
              optionsFormset.save()
            if backurl:
              return HttpResponseRedirect(backurl)
            if not field: # was inserted
              return HttpResponseRedirect(reverse(fieldEditor) + u'?id=' + unicode(form.instance.id))

  if form is None:
    form = FieldForm(instance=field)
    if not field or (field and field.fieldType == 'list'):
      optionsFormset = inlineformset_factory(Field, FieldOption, form=ModelForm)(instance=form.instance)

  if field is not None:
    form.addHidden('id', field.id)
  if backurl:
    form.addHidden('backurl', backurl)

  return render_to_response('field-editor.html', {
    'form': form,
    'optionsFormset': optionsFormset,
    'header_footer': HeaderFooter('fields'),
  })

