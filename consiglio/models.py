# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dateutil.utils import today
from django.utils import timezone
from django.contrib.gis.db import models
from django.contrib.gis.gdal import GDALRaster
from django.urls import reverse
from income.models import stazioni_retevista

from dash_aziende.models import campi as campi_agricoli
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
        verbose_name = 'Appezzamento old'
        verbose_name_plural = 'Appezzamenti old'

class appezzamentoCampo(models.Model):
    '''
    Nuovo modello per la gestione dell'appezzamento da campo inserito da parte di aziende agricole
    '''
    campi = models.ForeignKey(campi_agricoli)
    soglia = models.FloatField(default=5.0,verbose_name='tolleranza pioggia utile',help_text='espresso in mm')
    cap_di_campo = models.FloatField(verbose_name='capacità di campo', help_text='espresso in g/100g <br>celle C16',default=0)
    punto_appassimento = models.FloatField(verbose_name='punto di appassimento', help_text='espresso in g/100g <br>celle C17',default=0)
    den_app = models.FloatField(verbose_name='densità apparente del terreno',default=0.0,help_text='espresso in g/cm<sup>3</sup>')
    cap_idrica = models.FloatField(verbose_name='capacità idrica massima', help_text='celle C18 e C3',default=0)
    ris_fac_util = models.FloatField(verbose_name='riserva facilmente utilizzabile', help_text='espresso in mm<br>celle C4',default=0.0)
    vol_irriguo = models.FloatField(verbose_name='dose intervento irriguo',default=0)
    perc_riserva_util = models.PositiveIntegerField(verbose_name='percentuale riserva facilmente utilizzabile',
                                                    help_text='celle C5',default=1)
    data_apporto_irriguo = models.DateField(verbose_name='data ultimo apporto irriguo',default=timezone.now)
    volume_apporto_irriguo = models.PositiveIntegerField(verbose_name='volume dell\'ultimo apporto irriguo (mc)',default=10)
    kc_datasheet = models.FileField(upload_to='kc_spreadsheet', verbose_name='Kc csv file',
                                    default='kc_spreadsheet/Kc_elenco.csv')
    ks_datasheet = models.FileField(upload_to='ks_spreadsheet', verbose_name='Ks csv file',
                                    default='ks_spreadsheet/Kc_elenco.csv')
    data_semina = models.DateField(verbose_name='data di semina o trapianto',default=timezone.now)
    durata_ciclo = models.PositiveIntegerField(verbose_name='durata ciclo colturale (giorni)',default=1)
    strato_radici = models.FloatField(verbose_name='strato esplorato dalle radici (cm)',default=0.0)
    note = models.TextField(default='', blank=True, null=True)
    Airr_min = models.FloatField(default=0.0,blank=True,null=True,verbose_name='Soglia effettivo inizio intervento irriguo Airr_min',help_text='espresso in mm')
    Airr_minFlag = models.BooleanField(default=False,blank=True,verbose_name='Utilizzo valore di soglia intervento irriguo')

    def __str__(self):
        return "appezz: %s-%s-%s" %(self.campi.nome,self.campi.coltura,self.campi.proprietario)

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
    Ks = models.FloatField(default=1.0)
    Et0=models.FloatField(default=0.0,verbose_name='EvapoTraspirazione metodo esteso')
    Etc = models.FloatField(default=0.0)
    P_ep = models.FloatField(verbose_name='P - Ep (mm)',default=0.0)
    L = models.FloatField(default=0.0)
    Lambda = models.FloatField(default=0.0)
    a = models.FloatField(default=0.0)
    Au = models.FloatField(verbose_name='A>U mm',default=0.0)
    A = models.FloatField(default=0.0,verbose_name='capacità idrica massima',help_text='colonna L')
    Amin_irr = models.FloatField(default=40.0,verbose_name='Amin Irr',blank=True,null=True)
    Irrigazione = models.NullBooleanField(default=False,blank=True,null=True)
    dose = models.FloatField(default=0.0)
    dose_antropica = models.FloatField(default=0.0,verbose_name='Dose irrigua antropica (mm)')
    note = models.TextField(default='',blank=True,null=True)
    Irr_mm = models.FloatField(default=0.0,verbose_name='Irrigazione in mc')
    Irr_posticipata= models.BooleanField(default=False,verbose_name='Posticipa irrigazione')
    stazione = models.ForeignKey(stazioni_retevista)


    appezzamento = models.ForeignKey(appezzamento,null=True)
    appezzamentoDaCampo = models.ForeignKey(appezzamentoCampo,null=True)


    def get_absolute_url(self):
        return reverse('bilancio-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '%s %s' %( self.data_rif,self.appezzamentoDaCampo)

    class Meta:
        ordering = ('-data_rif',)
        verbose_name = 'Bilancio'
        verbose_name_plural = 'Bilanci'


class rasterAppezzamento(models.Model):
    '''
    modello per la catalogazione dei raster di CASA --unitus per consiglio azotato
    '''
    tipologia_choices = [
        ('OM', 'Sostanza organica'),
    ]
    appezzamento = models.ForeignKey(campi_agricoli,verbose_name='Appezzamento aziendale',help_text='Campo aziendale al quale associare il raster')
    raster = models.FileField(upload_to='rasterCasa',verbose_name='raster geotif',help_text='caricare un raster nel SR 4326 -- lat/long wgs84')
    titolo = models.CharField(max_length=250,verbose_name='Titolo del raster',help_text='inserire il titolo rappresentativo del raster')
    tipologia = models.CharField(max_length=250,choices=tipologia_choices,verbose_name='Tipologia del raster',default=tipologia_choices[0],blank=True,null=True)


    def __str__(self):
        return 'raster %s %s di %s' %(self.titolo,self.tipologia,self.appezzamento)



    def save(self, *args, **kwargs):
        #TODO: aggiungere i controlli sul raster
        super(rasterAppezzamento, self).save(*args, **kwargs)

    class Meta:
        verbose_name='Mappa raster'
        verbose_name_plural='Mappe raster'
        # order_with_respect_to = 'appezzamento'
        ordering = ['appezzamento']