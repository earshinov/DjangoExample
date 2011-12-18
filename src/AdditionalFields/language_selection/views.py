# -*- coding: utf-8 -*-

from AdditionalFields.HeaderFooter import HeaderFooter
from django.conf import settings
from django.shortcuts import render_to_response


def switchLanguage(request):
  return render_to_response('switch-language.html', {
    'languages': settings.LANGUAGES,
    'header_footer': HeaderFooter('language_selection'),
  })