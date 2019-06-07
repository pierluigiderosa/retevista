# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.db import models

# Create your models here.



class campi(models.Model):
    nome = models.CharField(max_length=250)
    coltura = models.CharField(max_length=250)
    geom = models.PolygonField(srid=4326)
    objects = models.GeoManager()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'campo'
        verbose_name_plural = 'campi'
