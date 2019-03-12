# - *- coding: utf- 8 - *-
from math import exp

import datetime as dt

from income.models import stazioni_retevista,dati_aggregati_daily
from consiglio.models import appezzamento
from consiglio.et_determination import ET_sistemista

from django.contrib.gis.db.models.functions import Distance
#TODO
#esempio di chiamata per ET determinazione:
#ET_sistemista(Z=100,Tmax=21.5,Tmin=12.3,RH_max=84,RH_min=63,SRmedia=255,U2=2.078,day='04032019',stazione=stazione)


def bilancio_idrico(pioggia,soglia=5,Kc=0,ctm_c9=55,ctm_c3=65,cap_id_max=55,area_irrigata_mq=3840,Et0=0):
    if pioggia>soglia:
        pioggia_5=pioggia
    else:
        pioggia_5=0


    # stazione = stazioni_retevista.objects.all()[0]
    # Et0=ET_sistemista(Z=100,Tmax=21.5,Tmin=12.3,RH_max=84,RH_min=63,SRmedia=255,U2=2.078,day='04032019',stazione=stazione)

    Etc=Et0*Kc

    if cap_id_max < ctm_c9:
        irrigazione = True
    else:
        irrigazione = False
    if irrigazione:
        dose = ctm_c3-cap_id_max  #va dato A giorno precedente
    else:
        dose=0

    #P-Ep
    if cap_id_max<ctm_c9:
        P_ep = dose - Etc + pioggia_5
    else:
        P_ep = pioggia_5 - Etc

    #L
    if P_ep>0:
        L=0
    else:
        L=P_ep

    Lambda=L/ctm_c3

    a=0
    if Lambda != 0:
        a=1.*cap_id_max/ctm_c3*exp(Lambda)

    #Au
    if a==0:
        Au = cap_id_max+P_ep
    else:
        Au = a * ctm_c3

    #A
    if Au>ctm_c3:
        A = ctm_c3
    else:
        A = Au

    #Irr_mm
    Irr_mm = None
    if irrigazione:
        Irr_mm = dose* area_irrigata_mq/1000.




        
    return dose, A, Irr_mm


def calc_bilancio():
    ieri = dt.datetime.today() - dt.timedelta(days=1)

    # prendo gli a appezzamenti
    appezzamenti=appezzamento.objects.all()
    #TODO -- debug prendo solo il primo: fare un ciclo for qui
    appezzam_singolo = appezzamenti[0]
    appezzam_pnt = appezzam_singolo.geom

    stazione_closest = stazioni_retevista.objects.annotate(
        distance=Distance('geom', appezzam_pnt)
    ).order_by('distance').first()

    dato_giornaliero = dati_aggregati_daily.objects.filter(data=ieri,stazione=stazione_closest)
    if dato_giornaliero.count()>1:
        dato_giornaliero = dato_giornaliero[0]

    # calcolo evapotraspirazione
    Tmax = dato_giornaliero.temp_max
    Tmin = dato_giornaliero.temp_min
    RH_max = dato_giornaliero.humrel_max
    RH_min = dato_giornaliero.humrel_min
    SRmedia = dato_giornaliero.solar_rad_mean
    vel_vento = dato_giornaliero.wind_speed_mean
    pioggia_cumulata = dato_giornaliero.rain_cumulata

    Et0 = ET_sistemista(Z=100, Tmax=Tmax, Tmin=Tmin, RH_max=RH_max, RH_min=RH_min, SRmedia=SRmedia, U2=vel_vento, day=ieri.strftime('%d%m%Y'),
                        stazione=stazione_closest)
    area = appezzam_singolo.settore.area
    dose, A, Irr_mm = bilancio_idrico(pioggia_cumulata,soglia=5,Kc=0,ctm_c9=55,ctm_c3=65,cap_id_max=55,area_irrigata_mq=appezzam_singolo.settore.area,Et0=Et0)


    return ieri,stazione_closest.nome,Tmax,Tmin,RH_max,RH_min,SRmedia,vel_vento,Et0,pioggia_cumulata,area, dose, A, Irr_mm