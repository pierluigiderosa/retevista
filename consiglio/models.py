# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.gis.db import models

# Create your models here.
from django.core.validators import MinValueValidator, MaxValueValidator




class coltura(models.Model):
    '''
    Modello della coltura

    specie	text
    data di semina o trapianto	data
    durata ciclo colturale	integer
    strato esplorato dalle radici	float double
    kc ini	float double
    kc med	float double
    kc end	float double
    durata giorni kc ini	float double
    durata giorni kc med	float double
    durata giorni kc end	float double
    '''

    specie = models.TextField()
    data_semina = models.DateField(verbose_name='data di semina o trapianto')
    durata_ciclo = models.PositiveIntegerField(verbose_name='durata ciclo colturale')
    strato_radici = models.FloatField(verbose_name='strato esplorato dalle radici')
    kc_ini = models.FloatField(verbose_name='Kc ini')
    kc_med= models.FloatField(verbose_name='Kc med')
    kc_end= models.FloatField(verbose_name='Kc end')
    durata_kc_ini= models.FloatField(verbose_name='durata giorni kc ini')
    durata_kc_med= models.FloatField(verbose_name='durata giorni kc med')
    durata_kc_end= models.FloatField(verbose_name='durata giorni kc end')

    def __str__(self):
        return self.specie

    class Meta:
        verbose_name='Coltura'
        verbose_name_plural='Colture'


class settore(models.Model):
    '''
    area	float double
    metodo irriguo	text
    data ultimo apporto irriguo	date
    volume dell'ultimo apporto irriguo	integer
    '''

    area = models.FloatField()
    metodo = models.TextField(verbose_name='metodo irriguo')
    data = models.DateField(verbose_name='data ultimo apporto irriguo')
    volume = models.PositiveIntegerField(verbose_name='volume dell\'ultimo apporto irriguo')

    def __str__(self):
        return self.metodo

    class Meta:
        verbose_name_plural='Settori'


class appezzamento(models.Model):
    '''
    Modello degli appezzamenti
    '''
    nome = models.TextField(verbose_name='nome appezzamento')
    conduttore = models.TextField()
    proprietario = models.TextField()
    localita =models.TextField(verbose_name='Località')
    coordinate  = models.FloatField()
    cap_di_campo  = models.FloatField(verbose_name='capacità di campo')
    punto_appassimento  = models.FloatField(verbose_name='punto di appassimento')
    perc_sabbia  = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)],verbose_name='percentuale sabbia')
    perc_argilla  = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)],verbose_name='percentuale argilla')
    perc_limo  = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)],verbose_name='percentuale limo')
    den_app = models.FloatField(verbose_name='densità apparente del terreno')
    cap_idrica = models.FloatField(verbose_name='capacità idrica utilizzabile')
    ris_fac_util = models.FloatField(verbose_name='riserva facilmente utilizzabile')
    vol_irriguo  = models.FloatField(verbose_name='volume intervento irriguo')
    perc_riserva_util = models.PositiveIntegerField(verbose_name='percentuale riserva facilmente utilizzabile')
    coltura = models.ForeignKey(coltura)
    settore = models.ForeignKey(settore)

    geom = models.PointField(srid=4326)
    objects = models.GeoManager()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Appezzamento'
        verbose_name_plural = 'Appezzamenti'
