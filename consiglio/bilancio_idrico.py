# - *- coding: utf- 8 - *-
from math import exp
import numpy as np
import datetime as dt

from income.models import stazioni_retevista,dati_aggregati_daily,quote_stazioni
from consiglio.models import appezzamento, bilancio
from consiglio.et_determination import ET_sistemista

from django.contrib.gis.db.models.functions import Distance



def line_eq(P1 = [100, 400],P2 = [240, 265],x=3):

    # Calculate the coefficients. This line answers the initial question.
    coefficients = np.polyfit(P1, P2, 1)

    # Print the findings
    # print 'a =', coefficients[0]
    a= coefficients[0]
    # print 'b =', coefficients[1]
    b = coefficients[1]

    y = a * x + b
    return y

def bilancio_idrico(pioggia,soglia=5,Kc=0,ctm_c7=55,ctm_c3=65,cap_id_max=55,area_irrigata_mq=3840,Et0=0):
    if pioggia>soglia:
        pioggia_5=pioggia
    else:
        pioggia_5=0


    Etc=Et0*Kc

    #ctm_c7 viene chiamato Airr_min
    #cap_id_max corrisponde alla colonna L
    if cap_id_max < ctm_c7:
        irrigazione = True
    else:
        irrigazione = False
    if irrigazione:
        dose = ctm_c3-cap_id_max  #va dato A giorno precedente
    else:
        dose=0

    #P-Ep
    if cap_id_max<ctm_c7:
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
    Irr_mm = 0
    if irrigazione:
        Irr_mm = dose* area_irrigata_mq/1000.




        
    return Etc,P_ep,L,Lambda,a,Au,A,dose, A, Irr_mm,irrigazione


def calc_Kc(coltura_id):
    from consiglio.models import coltura
    colture=coltura.objects.all()

    coltura_calcolo = colture.filter(id=coltura_id)
    #TODO controllo se non c'è la coltura...
    #new variables
    coltura_calcolo = coltura_calcolo.first()
    kc_ini = coltura_calcolo.kc_ini
    kc_med = coltura_calcolo.kc_med
    kc_end = coltura_calcolo.kc_end
    d_kc_ini = coltura_calcolo.durata_kc_ini
    d_kc_dev = coltura_calcolo.durata_kc_dev
    d_kc_med = coltura_calcolo.durata_kc_med
    d_kc_end = coltura_calcolo.durata_kc_end


    days_da_coltura = dt.date.today()-coltura_calcolo.data_semina
    j_coltura=None
    if days_da_coltura.days>1:
        j_coltura=days_da_coltura.days
    else:
        j_coltura=0
    Kc=None
    if j_coltura<=d_kc_ini:
        Kc=kc_ini
    elif j_coltura>d_kc_ini and j_coltura<=d_kc_dev+d_kc_ini:
        P1=[d_kc_ini,kc_ini]
        P2=[d_kc_dev+d_kc_ini,kc_med]
        Kc = line_eq(P1,P2,j_coltura)
    elif j_coltura > d_kc_dev+d_kc_ini and j_coltura<=d_kc_ini+d_kc_dev+d_kc_med:
        Kc=kc_med
    elif j_coltura > d_kc_ini + d_kc_dev + d_kc_med and j_coltura <= d_kc_ini + d_kc_dev + d_kc_med+d_kc_end:
        P1=[d_kc_ini + d_kc_dev + d_kc_med,kc_med]
        P2=[d_kc_ini + d_kc_dev + d_kc_med+d_kc_end,kc_end]
        Kc = line_eq(P1,P2,j_coltura)
    else:
        Kc=kc_end

    return Kc



def calc_bilancio():
    ieri = dt.date.today() - dt.timedelta(days=1)
    oggi =dt.date.today()

    # prendo gli a appezzamenti
    appezzamenti=appezzamento.objects.all()
    for appezzam_singolo in appezzamenti:

        appezzam_pnt = appezzam_singolo.geom

        stazione_closest = stazioni_retevista.objects.annotate(
            distance=Distance('geom', appezzam_pnt)
        ).order_by('distance').first()

        dato_giornaliero = dati_aggregati_daily.objects.filter(data=ieri,stazione=stazione_closest)
        if dato_giornaliero.count()>=1:
            dato_giornaliero = dato_giornaliero.first()

            # calcolo evapotraspirazione
            Tmax = dato_giornaliero.temp_max
            Tmin = dato_giornaliero.temp_min
            Tmean = dato_giornaliero.temp_mean
            RH_max = dato_giornaliero.humrel_max
            RH_min = dato_giornaliero.humrel_min
            SRmedia = dato_giornaliero.solar_rad_mean
            vel_vento = dato_giornaliero.wind_speed_mean
            pioggia_cumulata = dato_giornaliero.rain_cumulata
            quota =  quote_stazioni.objects.filter(stazioni=stazione_closest).first().quota
            Et0 = ET_sistemista(Z=quota, Tmax=Tmax, Tmin=Tmin, Tmean=Tmean, RH_max=RH_max, RH_min=RH_min, SRmedia=SRmedia, U2=vel_vento, day=ieri.strftime('%d%m%Y'), stazione=stazione_closest)
            Kc_calcolata = calc_Kc(appezzam_singolo.id)


            #calcolare cap_idrica_max che è la variabile A del giorno precedente, se assente è presente come dato in appezzamento
            bilancio_giorno_prec = bilancio.objects.filter(data_rif=ieri, stazione=stazione_closest)
            bilancio_odierno = bilancio.objects.filter(data_rif=oggi, stazione=stazione_closest)
            nota=''
            if bilancio_giorno_prec.count()==0:
                cap_id_max = appezzam_singolo.cap_idrica
                nota+='calcolo eseguito con cap id. max da valore appezzam.: '+str(cap_id_max)
            elif bilancio_giorno_prec.count()==1:
                cap_id_max= bilancio_giorno_prec[0].A
                nota += 'calcolo eseguito con cap id. max da giorno precedente.: ' + str(round(cap_id_max,2))
            area = appezzam_singolo.settore.area

            cap_id_util = appezzam_singolo.cap_idrica
            # ctm_c7 viene chiamato Airr_min
            Amin_Irr =cap_id_util-appezzam_singolo.ris_fac_util

            Etc,P_ep,L,Lambda,a,Au,A,dose, A, Irr_mm, irrigazione = bilancio_idrico(pioggia_cumulata,soglia=5,Kc=Kc_calcolata,ctm_c7=Amin_Irr,ctm_c3=cap_id_util,cap_id_max=cap_id_max,area_irrigata_mq=appezzam_singolo.settore.area,Et0=Et0)


            #salvataggio dati
            if bilancio_odierno.count()==0:
                nuovo_bilancio_giornaliero = bilancio(
                    data_rif=oggi,
                    pioggia_cum=pioggia_cumulata,
                    Kc = Kc_calcolata,
                    Et0 = Et0,
                    Etc = Et0*Kc_calcolata,
                    P_ep = P_ep,
                    L = L,
                    Lambda = Lambda,
                    a = a,
                    Au = Au,
                    A = A,
                    Irrigazione = irrigazione,
                    dose = dose,
                    Irr_mm = Irr_mm,
                    stazione = stazione_closest,
                    appezzamento = appezzam_singolo,
                    note=nota,
                )
                nuovo_bilancio_giornaliero.save()

            return ieri,stazione_closest.nome,Tmax,Tmin,RH_max,RH_min,SRmedia,vel_vento,Et0,pioggia_cumulata,cap_id_util,area, dose, A, Irr_mm