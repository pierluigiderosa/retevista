# - *- coding: utf- 8 - *-
import socket
from math import exp
import numpy as np
import datetime as dt
from django.core.mail import send_mail

from income.models import stazioni_retevista,dati_aggregati_daily,quote_stazioni
from consiglio.models import appezzamento, bilancio,appezzamentoCampo
from consiglio.et_determination import ET_sistemista

from django.contrib.gis.db.models.functions import Distance
from pandas import Series


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

def costanteTerrenoModificata(PA,CC,den_app,stratoRadicale,RFUperc=50):
    '''

    :param PA: punto di appassimento - cella C11 foglio
    :param CC: capacità di campo - cella C12 foglio
    :param den_app: densità apparente - cella c13 foglio
    :param stratoRadicale: strato esplorato dalle radici - cella c14 foglio
    :RFUperc
    :return:
    '''

    CCmodificato =(10000.*(CC*0.01)*den_app*stratoRadicale)*0.1
    PAmodificato =(10000.*(PA*0.01)*den_app*stratoRadicale)*0.1
    # capacità idrica utilizzabile
    U = CCmodificato-PAmodificato
    RFU = RFUperc*U/100.
    Airr_min = U - RFU
    print CCmodificato,PAmodificato,U,RFU,Airr_min
    return CCmodificato,PAmodificato,U,RFU,Airr_min

def bilancio_idrico(pioggia, soglia=5, Kc=0, ctm_c7=55, ctm_c3=65,
                    A_day_precedente=55, area_irrigata_mq=3840, Et0=0, dose_antropica=0,
                    posticipa=False,
                    nomeApp=None,
                    idAppezzamento=None,
                    Irrigazione_giorno_precedente=False,
                    email=None):
    if pioggia>soglia:
        pioggia_5=pioggia
    else:
        pioggia_5=0


    Etc=Et0*Kc
    P_ep = pioggia_5 - Etc + dose_antropica

    #L
    if P_ep>0:
        L=0
    else:
        L=P_ep

    Lambda=L/ctm_c3

    a=0
    if Lambda != 0:
        a= 1. * A_day_precedente / ctm_c3 * exp(Lambda)

    #Au
    if a==0:
        Au = A_day_precedente + P_ep
    else:
        Au = a * ctm_c3

    #A
    if Au>ctm_c3:
        A = ctm_c3
    else:
        A = Au

    #ctm_c7 viene chiamato Airr_min
    #cap_id_max corrisponde alla colonna M
    if A < ctm_c7:
        irrigazione = True
        if socket.gethostname() == 'pierluigidero':
            #invio mail
            send_mail(
                'Avvio procedura di irrigazione campo {}'.format(nomeApp),
                '''Si deve avviare la procedura di irrigazione al campo {}.\b PC di invio {}<br>
                Vai alla pagina http://www.onegis.it/retevista/elaborazioni/infocampo/{} per inserire la dose.
                '''.format(nomeApp,socket.gethostname(),idAppezzamento),
                'retevista@gmail.com',
                ['pierluigi.derosa@gmail.com','peppoloni.francy@gmail.com'], #in definitiva mettere email
                fail_silently=False,
            )
        pass
    else:
        irrigazione = False

    #P - Ep controllato con irrigazione
    dose = 0
    if irrigazione:
        if posticipa is False and dose_antropica==0: # and Irrigazione_giorno_precedente is True:
            dose = ctm_c3 - A #modificato A_day_precedente  #va dato A giorno precedente

        P_ep = pioggia_5 - Etc + dose_antropica +dose

        # L
        if P_ep > 0:
            L = 0
        else:
            L = P_ep

        Lambda = L / ctm_c3

        a = 0
        if Lambda != 0:
            a = 1. * A_day_precedente / ctm_c3 * exp(Lambda)

        # Au
        if a == 0:
            Au = A_day_precedente + P_ep
        else:
            Au = a * ctm_c3

        # A
        if Au > ctm_c3:
            A = ctm_c3
        else:
            A = Au





    #Irr_mm
    Irr_mc_ha = 0
    if irrigazione:
        Irr_mc_ha = dose* area_irrigata_mq/1000.




        
    return Etc,P_ep,L,Lambda,a,Au,A,dose, A, Irr_mc_ha,irrigazione


def calc_Kc(coltura_id):
    '''
    funzione per il calcolo di Ks a partire da parametri noti. Adesso l'implemetazione è stata modificata.
    Obsoleta e non utilizzata
    '''
    from consiglio.models import coltura
    colture=coltura.objects.all()

    coltura_calcolo = colture.filter(id=coltura_id)
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

def calc_Kc_elenco(coltura_id):
    from consiglio.models import coltura
    colture = coltura.objects.all()

    coltura_calcolo = colture.filter(id=coltura_id)
    coltura_calcolo = coltura_calcolo.first()

    serie = Series.from_csv(coltura_calcolo.kc_datasheet.path, header=0, parse_dates=['data'])

    # accesso al giorno
    Kc = serie[dt.date.today().strftime('%d/%m/%Y')][0]
    return Kc

def calc_bilancio_campo():
    '''
    Funzione che calcola il bilancio ogni mattina per il giorno corrente
    :return:
    '''

    ieri = dt.date.today() - dt.timedelta(days=1)
    oggi =dt.date.today()

    # prendo gli a appezzamenti
    appezzamentoCampi = appezzamentoCampo.objects.all()
    for app_campo in appezzamentoCampi:
        #get geometri from appezzamento
        poligono_campo = app_campo.campi.geom
        appezzam_pnt = poligono_campo.centroid
        soglia = app_campo.soglia

        stazione_closest = stazioni_retevista.objects.annotate(
            distance=Distance('geom', appezzam_pnt)
        ).order_by('distance').first()
        dato_giornaliero = dati_aggregati_daily.objects.filter(data=ieri,stazione=stazione_closest)
        print oggi
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
            # quota =  quote_stazioni.objects.filter(stazioni=stazione_closest).first().quota
            quota=float(stazione_closest.quota)
            Et0 = ET_sistemista(Z=quota, Tmax=Tmax, Tmin=Tmin, Tmean=Tmean, RH_max=RH_max, RH_min=RH_min, SRmedia=SRmedia, U2=vel_vento, day=ieri.strftime('%d%m%Y'), stazione=stazione_closest)
            print('id coltura:')
            print(app_campo.campi.coltura.id)
            serieKc = Series.from_csv(app_campo.kc_datasheet.path,header=0,parse_dates=['data'])
            #TODO correggere Ks
            # serieKs = Series.from_csv(app_campo.ks_datasheet.path,header=0,parse_dates=['data'])
            # Ks = serieKs[ieri.strftime('%d/%m/%Y')][0]
            Kc = serieKc[ieri.strftime('%d/%m/%Y')][0]
            Kc_calcolata = Kc*1
            print 'Kc= '
            print Kc_calcolata


            #calcolare cap_idrica_max che è la variabile A del giorno precedente, se assente è presente come dato in appezzamento
            bilancio_giorno_prec = bilancio.objects.filter(data_rif=ieri, appezzamentoDaCampo=app_campo)
            bilancio_odierno = bilancio.objects.filter(data_rif=oggi, appezzamentoDaCampo=app_campo)
            nota=''

            posticipa_Irr = None
            Irrigazione_giorno_precedente = False
            # dose antropica per irrigazione forzata
            if bilancio_giorno_prec.count()==0:
                cap_id_max = app_campo.cap_idrica
                nota+='calcolo eseguito con cap id. max da valore appezzam.: '+str(cap_id_max)
                dose_antropica = 0
                posticipa_Irr = False
            elif bilancio_giorno_prec.count()==1:
                cap_id_max= bilancio_giorno_prec[0].A
                nota += 'calcolo eseguito con cap id. max da giorno precedente.: ' + str(round(cap_id_max,2))
                dose_antropica = bilancio_giorno_prec[0].dose_antropica
                posticipa_Irr = bilancio_giorno_prec[0].Irr_posticipata
                Irrigazione_giorno_precedente = bilancio_giorno_prec[0].Irrigazione
            app_campo.campi.geom.transform(3004, clone=False)
            areaCampo = app_campo.campi.geom.area


            #nuova implementazione
            if app_campo.campi.analisi_suolo_set.exists():
                analisi = app_campo.campi.analisi_suolo_set.first()
                cap_di_campo_Analisi = analisi.cap_di_campo
                punto_appassimentoAnalisi = analisi.punto_appassimento
                den_apparenteAnalisi = analisi.den_apparente
            else:
                cap_di_campo_Analisi = app_campo.cap_di_campo
                punto_appassimentoAnalisi = app_campo.punto_appassimento
                den_apparenteAnalisi = app_campo.den_app
            strato_radici = app_campo.strato_radici
            RFUperc = app_campo.perc_riserva_util
            CCmodificato, PAmodificato, U, RFU, Airr_min = costanteTerrenoModificata(
                PA=punto_appassimentoAnalisi,
                CC=cap_di_campo_Analisi,
                den_app=den_apparenteAnalisi,
                stratoRadicale=strato_radici / 100., RFUperc=RFUperc)


            cap_id_util=U
            #cap_id_util = app_campo.cap_idrica #versione prima modifica calcolo automatico
            #cap_id_util deve essere U da costante terreno modificata

            # ctm_c7 viene chiamato Airr_min
            # Airr_min =cap_id_util-app_campo.ris_fac_util #versione prima modifica calcolo automatico
            #Amin_irr deve essere letto da calcolo

            Etc,P_ep,L,Lambda,a,Au,A,dose, A, Irr_mm, irrigazione = bilancio_idrico(pioggia_cumulata,
                                                                                    soglia=soglia,
                                                                                    Kc=Kc_calcolata,
                                                                                    ctm_c7=Airr_min,  #da calcolo
                                                                                    ctm_c3=cap_id_util,  #da calcolo U
                                                                                    A_day_precedente=cap_id_max,
                                                                                    area_irrigata_mq=areaCampo,
                                                                                    Et0=Et0,
                                                                                    dose_antropica = dose_antropica,
                                                                                    posticipa= posticipa_Irr,
                                                                                    nomeApp=app_campo.campi.nome,
                                                                                    idAppezzamento=app_campo.id,
                                                                                    Irrigazione_giorno_precedente=Irrigazione_giorno_precedente,
                                                                                    email=app_campo.campi.proprietario.user.email)


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
                    Amin_irr = cap_id_max,
                    A = A,
                    Irrigazione = irrigazione,
                    dose = dose,
                    Irr_mm = Irr_mm,
                    stazione = stazione_closest,
                    appezzamentoDaCampo = app_campo,
                    note=nota,
                )
                nuovo_bilancio_giornaliero.save()

            print(ieri,stazione_closest.nome,Tmax,Tmin,RH_max,RH_min,SRmedia,vel_vento,Et0,pioggia_cumulata,cap_id_util,areaCampo, dose, A, Irr_mm)
            print('irrigazione giorno precedente: {}'.format(Irrigazione_giorno_precedente))