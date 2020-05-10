# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from dash_aziende.models import Profile, ColturaDettaglio


# Create your models here.

class prenotazione(models.Model):
    acquirente = models.ForeignKey(Profile)
    quantita = models.FloatField(default=0,verbose_name='Quantità da prenotare')
    coltura = models.ForeignKey(ColturaDettaglio)

    class Meta:
        verbose_name_plural = 'prenotazioni'

    def __str__(self):
        return "%s : %s" %(self.acquirente,self.quantita)

