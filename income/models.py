# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.gis.db import models


# Create your models here.

class stazioni_retevista(models.Model):
    lat = models.FloatField()
    long = models.FloatField()
    nome = models.CharField(max_length=20)
    did = models.CharField(max_length=25)
    geom = models.MultiPointField(srid=4326)
    objects = models.GeoManager()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'stazione'
        verbose_name_plural = 'stazioni'


class dati_orari(models.Model):
    # 'Date & Time', 'Rain Rate - mm', 'Temp - C']
    pioggia = models.FloatField()
    EvapoTras = models.FloatField()
    windSpeed = models.FloatField()
    humRel = models.FloatField()
    pressione = models.FloatField()
    solarRad = models.FloatField()
    dataora = models.DateTimeField()
    rainrate = models.FloatField(default=0.0)
    temp = models.FloatField(default=0.0)

    def __str__(self):
        return self.dataora

    class Meta:
          ordering = ('-dataora',) # helps in alphabetical listing. Sould be a tuple
