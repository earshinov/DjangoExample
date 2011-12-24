# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from fields.models import Field
from fields.forms import FieldForm
from DjangoExample.HeaderFooter import HeaderFooter


def fieldList(request):
  return render_to_response('field-list.html',
    {
      'fields': Field.objects.all(),
      'header_footer': HeaderFooter('fields'),
    },
    context_instance=RequestContext(request))


def fieldEditor(request):

  field = None
  instanceId = request.REQUEST.get('id')
  if instanceId:
    field = get_object_or_404(Field, pk=instanceId)

  backurl = request.REQUEST.get('backurl')

  form = None
  if request.method == 'POST':
    if field and 'delete' in request.POST:
      field.delete()
      if backurl:
        return HttpResponseRedirect(backurl)
      return HttpResponseRedirect(reverse(fieldEditor))
    else:
      form = FieldForm(request.POST, instance=field)
      if 'save' in request.POST and form.is_valid():
        if field:
          # Указываем force_update, чтобы сэкономить один ненужный
          # SQL-запрос на проверку существования записи в базе
          form.save(commit=False)
          field.save(force_update=True)
        else:
          form.save()
        if backurl:
          return HttpResponseRedirect(backurl)
        if not field: # was inserted
          return HttpResponseRedirect(reverse(fieldEditor) + u'?id=' + unicode(form.instance.id))

  if form is None:
    form = FieldForm(instance=field)
  if field is not None:
    form.addHidden('id', field.id)
  if backurl:
    form.addHidden('backurl', backurl)

  return render_to_response('field-editor.html', {
    'form': form,
    'header_footer': HeaderFooter('fields'),
  })

