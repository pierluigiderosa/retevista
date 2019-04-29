# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.gis.db import models

# Create your models here.
from django.urls import reverse
from django_pandas.managers import DataFrameManager


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

class dati_aggregati_daily(models.Model):
    rain_cumulata = models.FloatField(blank=True,null=True,help_text='pioggia cumulata giornaliera',verbose_name='pioggia cum. giornaliera')
    temp_min = models.FloatField(blank=True,null=True,verbose_name='Temp. min.')
    temp_max = models.FloatField(blank=True,null=True,verbose_name='Temp. max')
    temp_mean = models.FloatField(blank=True,null=True,verbose_name='Temp media')
    humrel_min = models.FloatField(blank=True,null=True,verbose_name='Umid. rel. min')
    humrel_max = models.FloatField(blank=True,null=True,verbose_name='Umid. rel. max')
    solar_rad_mean =  models.FloatField(blank=True,null=True,verbose_name='radiazione solare')
    wind_speed_mean = models.FloatField(blank=True,null=True,verbose_name='Velocità vento media')
    stazione = models.ForeignKey(stazioni_retevista,default=1,null=True)
    note = models.CharField(default='',verbose_name='Note',max_length=2500)
    data = models.DateField(verbose_name='Data')

    def get_absolute_url(self):
        return reverse('dato-daily-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '%s %s' % (str(self.stazione),str(self.data))

    class Meta:
          ordering = ('-data',)



class dati_orari(models.Model):
    # 'Date & Time', 'Rain Rate - mm', 'Temp - C']
    pioggia = models.FloatField(blank=True,null=True,help_text='pioggia cumulata giornaliera')
    EvapoTras = models.FloatField(blank=True,null=True,verbose_name='Evapotraspirazione')
    windSpeed = models.FloatField(blank=True,null=True,verbose_name='Velocità del vento')
    humRel = models.FloatField(blank=True,null=True,verbose_name='Umidità relativa')
    pressione = models.FloatField(blank=True,null=True,verbose_name='Pressione atm.')
    solarRad = models.FloatField(blank=True,null=True,verbose_name='Radiazione solare')
    dataora = models.DateTimeField(blank=True,null=True,verbose_name='Data & Ora')
    rainrate = models.FloatField(default=0.0,blank=True,null=True,verbose_name='Intesità di pioggia ')
    temp = models.FloatField(default=0.0,blank=True,null=True,verbose_name='Temperatura °C')
    et_cum_year = models.FloatField(default=0.0, blank=True, null=True, verbose_name='Et cum annuale')
    et_cum_month = models.FloatField(default=0.0, blank=True, null=True, verbose_name='Et cum mensile')
    et_cum_day = models.FloatField(default=0.0, blank=True, null=True, verbose_name='Et cum giornaliera')
    rain_cum_year = models.FloatField(default=0.0,blank=True,null=True,verbose_name='Rain cum annuale')
    rain_cum_month = models.FloatField(default=0.0, blank=True, null=True, verbose_name='Rain cum mensile')
    rain_cum_day = models.FloatField(default=0.0, blank=True, null=True, verbose_name='Rain cum giornaliera')
    stazione = models.ForeignKey(stazioni_retevista,default=1,null=True)

    objects = DataFrameManager()

    def __str__(self):
        return '%s' %(str(self.dataora))

    class Meta:
          ordering = ('-dataora',) # helps in alphabetical listing. Sould be a tuple


class quote_stazioni(models.Model):
    stazioni = models.OneToOneField(stazioni_retevista)
    quota = models.FloatField(default=300)

    def __str__(self):
        return 'quota: %s' % (self.stazioni)