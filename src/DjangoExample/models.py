# -*- coding: utf-8 -*-

from django.db import models


# Наш базовый класс модели. Конкретные модели должны наследоваться
# от этого класса, а не от django.db.models.Model
class Model(models.Model):

  class Meta:
    # Чтобы этот класс модели не считался связанным с какой-либо таблицей в БД
    abstract = True

  # Если у записи есть идентификатор, при сохранении задаём флажок force_update.
  # Это заставляет Django не делать дополнительный запрос на существование объекта
  def save(self, force_insert=False, force_update=False, using=None):
    if not force_insert and not force_update and getattr(self, self._meta.pk.attname) is not None:
      force_update = True
    return super(Model, self).save(force_insert, force_update, using)
