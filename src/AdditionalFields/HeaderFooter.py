from copy import deepcopy
from django.utils.translation import ugettext_lazy as _


class HeaderFooter(object):
  
  class SiteSection(object):
    
    def __init__(self, code, name, defaultPage, selected=False):
      object.__init__(self)
      self.code = code
      self.name = name
      self.default_page = defaultPage
      self.selected = selected
  
  SITE_SECTIONS = [
    SiteSection('fields', _('Fields'), '/field-list/'),
    SiteSection('language_selection', _('Language Selection'), '/switch-language/'),
  ]
  
  def __init__(self, siteSectionCode):
    self.site_sections = deepcopy(self.SITE_SECTIONS)
    for section in self.site_sections:
      if section.code == siteSectionCode:
        section.selected = True
        break