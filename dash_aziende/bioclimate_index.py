# -*- coding: utf-8 -*-

'''
modulo python per realizzare gli indici bioclimatici
in input accetto id della stazione meteo
'''
from dash_aziende.models import campi
from income.models import dati_aggregati_daily, dati_orari, stazioni_retevista
from datetime import date, datetime,time
from django.contrib.gis.db.models.functions import Distance

def get_station(idCampo):
    # devo trovare la stazione più vicina al campo richiesto:
    campo = campi.objects.get(id=idCampo)
    stazione_closest = stazioni_retevista.objects.annotate(
        distance=Distance('geom', campo.geom.centroid)
    ).order_by('distance').first()
    return stazione_closest

def Winkler(idCampo):
    '''
    Tmed = temperatura media giornaliera da 1 aprile a 31 ottobre
    :param idCampo:
    :return:
    '''

    anno_corrente=datetime.today().year
    fine = date(year=anno_corrente, month=10, day=31)

    # controllo che fine periodo sia prima della data odierna
    if fine > datetime.today().date():
        anno_corrente=anno_corrente-1
    inizio= date(year=anno_corrente,month=4,day=1)
    fine = date(year=anno_corrente,month=10,day=31)

    #prendo ola stazione più vicina
    stazione = get_station(idCampo)

    dati_giornalieri = dati_aggregati_daily.objects.filter(stazione=stazione, data__gte=inizio, data__lte=fine)

    #indice di Winkler
    IW = 0
    for dato_giorno in dati_giornalieri:
        if dato_giorno.temp_mean > 10:
            IW = IW + dato_giorno.temp_mean-10

    return IW

def Huglin(idcampo):
    '''
    Indice di Huglin
    :param idcampo:
    :return:
    '''

    anno_corrente=datetime.today().year
    fine = date(year=anno_corrente, month=9, day=30)

    #controllo che fine periodo sia prima della data corrente
    if fine > datetime.today().date():
        anno_corrente=anno_corrente-1
    fine = date(year=anno_corrente, month=9, day=30)
    inizio= date(year=anno_corrente,month=4,day=1)

    # devo trovare la stazione più vicina al campo richiesto:
    stazione = get_station(idcampo)

    dati_giornalieri = dati_aggregati_daily.objects.filter(stazione=stazione, data__gte=inizio, data__lte=fine)

    # Indice di Huglin
    IH = 0
    for dato_giornaliero in dati_giornalieri:
        Tmed = dato_giornaliero.temp_mean
        Tmax = dato_giornaliero.temp_max
        K = 1.03 # Per Umbria
        IH = IH + (((Tmed-10)+(Tmax-10))/2)*K

    return IH


def Fregoni(idCampo):
    anno_corrente = datetime.today().year
    fine = date(year=anno_corrente, month=9, day=30)

    # controllo che fine periodo sia prima della data corrente
    if fine > datetime.today().date():
        anno_corrente = anno_corrente - 1
    fine = date(year=anno_corrente, month=9, day=30)
    inizio = date(year=anno_corrente, month=9, day=1)

    # prendo la stazione più vicina
    stazione = get_station(idCampo)
    dati_giornalieri = dati_aggregati_daily.objects.filter(stazione=stazione, data__gte=inizio, data__lte=fine)

    # Indice di Fregoni
    IF = 0
    for dato_giornaliero in dati_giornalieri:
        Tmin = dato_giornaliero.temp_min
        Tmax = dato_giornaliero.temp_max

        # CONTEGGIO LE ORE CON TEMPERATURA SUPERIORE A 10°
        ora_inizio = datetime.combine(dato_giornaliero.data, time.min)
        ora_fine = datetime.combine(dato_giornaliero.data, time.max)
        h = dati_orari.objects.filter(stazione=stazione, dataora__gte=ora_inizio, dataora__lte=ora_fine,
                                      temp__gte=10).count()

        IF = IF + ((Tmax-Tmin)*h)

    return IF