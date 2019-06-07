# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dateutil.utils import today
from django.contrib.gis.db import models
from django.urls import reverse
from income.models import stazioni_retevista

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
    durata_ciclo = models.PositiveIntegerField(verbose_name='durata ciclo colturale (giorni)')
    strato_radici = models.FloatField(verbose_name='strato esplorato dalle radici (cm)')
    kc_ini = models.FloatField(verbose_name='Kc ini',default=0)
    kc_med= models.FloatField(verbose_name='Kc med',default=0)
    kc_end= models.FloatField(verbose_name='Kc end',default=0)
    durata_kc_ini= models.FloatField(verbose_name='durata giorni kc ini',default=0)
    durata_kc_dev= models.FloatField(verbose_name='durata giorni kc dev',default=1.0)
    durata_kc_med= models.FloatField(verbose_name='durata giorni kc med',default=0)
    durata_kc_end= models.FloatField(verbose_name='durata giorni kc end',default=0)
    kc_datasheet = models.FileField(upload_to='kc_spreadsheet',verbose_name='Kc csv file',default='kc_spreadsheet/Kc_elenco.csv')

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

    area = models.FloatField(verbose_name='area mq',help_text='area  in metri quadri')
    metodo = models.TextField(verbose_name='metodo irriguo')
    data = models.DateField(verbose_name='data ultimo apporto irriguo')
    volume = models.PositiveIntegerField(verbose_name='volume dell\'ultimo apporto irriguo (mc)')

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
    soglia  = models.FloatField(default=5.0)
    cap_di_campo  = models.FloatField(verbose_name='capacità di campo',help_text='celle C16')
    punto_appassimento  = models.FloatField(verbose_name='punto di appassimento',help_text='celle C17')
    perc_sabbia  = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)],verbose_name='percentuale sabbia')
    perc_argilla  = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)],verbose_name='percentuale argilla')
    perc_limo  = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)],verbose_name='percentuale limo')
    den_app = models.FloatField(verbose_name='densità apparente del terreno')
    cap_idrica = models.FloatField(verbose_name='capacità idrica massima',help_text='celle C18 e C3')
    ris_fac_util = models.FloatField(verbose_name='riserva facilmente utilizzabile',help_text='celle C4')
    vol_irriguo  = models.FloatField(verbose_name='dose intervento irriguo')
    perc_riserva_util = models.PositiveIntegerField(verbose_name='percentuale riserva facilmente utilizzabile',help_text='celle C5')
    coltura = models.ForeignKey(coltura)
    settore = models.ForeignKey(settore)

    geom = models.PointField(srid=4326)
    objects = models.GeoManager()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Appezzamento'
        verbose_name_plural = 'Appezzamenti'


class bilancio(models.Model):
    '''
    Modello per il salvataggio del bilancio idrologico
    '''
    data_rif = models.DateField(verbose_name='data calcolo bilancio',default=today)
    pioggia_cum=models.FloatField(verbose_name='pioggia cumulata',default=0.0)
    Kc = models.FloatField(default=0.0)
    Et0=models.FloatField(default=0.0,verbose_name='EvapoTraspirazione metodo esteso')
    Etc = models.FloatField(default=0.0)
    P_ep = models.FloatField(verbose_name='P - Ep (mm)',default=0.0)
    L = models.FloatField(default=0.0)
    Lambda = models.FloatField(default=0.0)
    a = models.FloatField(default=0.0)
    Au = models.FloatField(verbose_name='A>U mm',default=0.0)
    A = models.FloatField(default=0.0,verbose_name='capacità idrica massima',help_text='colonna L')
    Irrigazione = models.NullBooleanField(default=False,blank=True,null=True)
    dose = models.FloatField(default=0.0)
    dose_antropica = models.FloatField(default=0.0,verbose_name='Dose irrigua antropica (mm)')
    note = models.TextField(default='',blank=True,null=True)
    Irr_mm = models.FloatField(default=0.0,verbose_name='Irrigazione in mc')
    stazione = models.ForeignKey(stazioni_retevista)


    appezzamento = models.ForeignKey(appezzamento)


    def get_absolute_url(self):
        return reverse('bilancio-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '%s %s' %( self.data_rif,self.appezzamento.nome)

    class Meta:
        ordering = ('-data_rif',)
        verbose_name = 'Bilancio'
        verbose_name_plural = 'Bilanci'
