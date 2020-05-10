# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime,timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.gis.db.models.functions import Distance
from django.http import Http404, HttpResponse, JsonResponse

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django_common.mixin import LoginRequiredMixin

from consiglio.models import appezzamento,bilancio,appezzamentoCampo,rasterAppezzamento
from dash_aziende.models import campi
from income.models import stazioni_retevista, dati_aggregati_daily
from .WriteToExcel import WriteToExcel
from consiglio.bilancio_idrico import costanteTerrenoModificata
from .forms import BilancioForm, RasterCasaForm
from bootstrap_modal_forms.generic import (
                                           BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)
from django.contrib.gis.gdal import GDALRaster


# Create your views here.

def lista_appezzamenti(request):

    #prima utilizzavo i vecchi appezzamenti
    # lista_appez = appezzamento.objects.all()
    lista_appezCampo = appezzamentoCampo.objects.all()

    #todo test calcolo capacità di campo
    # qua si capisce da dove provengono i dati per calcolare la cap di campo
    cap_di_campo_list = []
    punto_appassimento_list = []
    den_appassimento_list = []
    strato_radici_list = []
    RFUperc_list = []
    CCmodificato_list = []
    PAmodificato_list = []
    U_list = []
    RFU_list=[]
    Airr_min_list = []
    for app_campo in lista_appezCampo:
        if app_campo.campi.analisi_suolo_set.exists():
            analisi = app_campo.campi.analisi_suolo_set.first()
            cap_di_campo_Analisi = analisi.cap_di_campo
            punto_appassimentoAnalisi =analisi.punto_appassimento
            den_apparenteAnalisi = analisi.den_apparente
        else:
            cap_di_campo_Analisi = app_campo.cap_di_campo
            punto_appassimentoAnalisi = app_campo.punto_appassimento
            den_apparenteAnalisi = app_campo.den_app
        strato_radici = app_campo.strato_radici
        RFUperc = app_campo.perc_riserva_util
        CCmodificato,PAmodificato,U,RFU,Airr_min = costanteTerrenoModificata(
            PA=punto_appassimentoAnalisi,
            CC=cap_di_campo_Analisi,
            den_app=den_apparenteAnalisi,
            stratoRadicale=strato_radici/100.,RFUperc=RFUperc)
        # append data to lists
        cap_di_campo_list.append(cap_di_campo_Analisi)
        punto_appassimento_list.append(punto_appassimentoAnalisi)
        den_appassimento_list.append(den_apparenteAnalisi)
        strato_radici_list.append(strato_radici)
        RFUperc_list.append(RFUperc)
        CCmodificato_list.append(CCmodificato)
        PAmodificato_list.append(PAmodificato)
        U_list.append(U)
        RFU_list.append(RFU)
        Airr_min_list.append(Airr_min)
        total =zip(lista_appezCampo,cap_di_campo_list,punto_appassimento_list,
                   den_appassimento_list,strato_radici_list,RFUperc_list,
                   CCmodificato_list,PAmodificato_list,U_list,RFU_list,Airr_min_list)

    # ieri,stazione_nome,Tmax,Tmin,RH_max,RH_min,SRmedia,vel_vento,Et0,pioggia,cap_id_zero,area,dose, A, Irr_mm = calc_bilancio()

    context = {

        'appez_campo':total,
        # 'appez_campo':lista_appezCampo,
        # 'cap_di_campo':cap_di_campo_list,
        # 'punto_appassimento':punto_appassimento_list,
        # 'den_apparente':den_appassimento_list,
        # 'strato_radici':strato_radici_list,
        # 'RFU':RFUperc_list,
        # 'ieri': ieri.strftime('%d/%m/%Y'),
        # 'stazione_nome': stazione_nome,
        # 'Tmax': Tmax,
        # 'Tmin': Tmin,
        # 'RH_max': RH_max,
        # 'RH_min': RH_min,
        # 'SRmedia': SRmedia,
        # 'vel_vento':vel_vento,
        # 'Et0':Et0,
        # 'pioggia': pioggia,
        # 'cap_id_zero': cap_id_zero,
        # 'area': area,
        # 'dose': dose,
        # 'A': A,
        # 'Irr_mm': Irr_mm,
    }
    return render(request, 'lista_appezzamenti.html', context)


def singolo_appezz(request,uid=99):
    try:
        UID = int(uid)
    except ValueError:
        raise Http404()
    appez_riferimento = appezzamento.objects.get(pk=UID)
    bilancio_appezzam = bilancio.objects.filter(appezzamento=uid)
    soglia_intervento = appez_riferimento.cap_idrica-appez_riferimento.ris_fac_util

    context ={
        'nome_app':appez_riferimento.nome,
        'app_id':UID,
        'cap_idricamax':appez_riferimento.cap_idrica,
        'bilancio_appezzam':bilancio_appezzam,
        'soglia':soglia_intervento,
    }

    return render(request,'singolo_appez.html',context)

def singolo_appezz_campo(request,uid=999):
    try:
        UID = int(uid)
    except ValueError:
        raise Http404()
    appez_riferimento = appezzamentoCampo.objects.get(pk=UID)
    bilancio_appezzam = bilancio.objects.filter(appezzamentoDaCampo=UID)
    soglia_intervento = appez_riferimento.cap_idrica - appez_riferimento.ris_fac_util
    context = {
        'nome_app': appez_riferimento.campi.nome,
        'app_id': UID,
        'cap_idricamax': appez_riferimento.cap_idrica,
        'bilancio_appezzam': bilancio_appezzam,
        'soglia': soglia_intervento,
    }

    return render(request, 'singolo_appez.html', context)

def infoViewCampo(request,uid=999):
    try:
        UID = int(uid)
    except ValueError:
        raise Http404()
    appez_riferimento = appezzamentoCampo.objects.get(pk=UID)
    bilancio_appezzam = bilancio.objects.filter(appezzamentoDaCampo=UID).first()
    ultimo_intervento_irriguo = bilancio.objects.filter(appezzamentoDaCampo=UID,Irrigazione=True,dose_antropica__gt=0).first()

    #calcolo giorni ciclo colturale
    if ultimo_intervento_irriguo is not None:
        delta = datetime.now().date() - ultimo_intervento_irriguo.data_rif
        giorni = delta.days
    else:
        giorni = 'Mai irrigato'
    # calcolo di U e Amin_irr
    if appez_riferimento.campi.analisi_suolo_set.exists():
        analisi = appez_riferimento.campi.analisi_suolo_set.first()
        cap_di_campo_Analisi = analisi.cap_di_campo
        punto_appassimentoAnalisi = analisi.punto_appassimento
        den_apparenteAnalisi = analisi.den_apparente
    else:
        cap_di_campo_Analisi = appez_riferimento.cap_di_campo
        punto_appassimentoAnalisi = appez_riferimento.punto_appassimento
        den_apparenteAnalisi = appez_riferimento.den_app

    strato_radici = appez_riferimento.strato_radici
    RFUperc = appez_riferimento.perc_riserva_util
    CCmodificato, PAmodificato, U, RFU, Airr_min = costanteTerrenoModificata(
        PA=punto_appassimentoAnalisi,
        CC=cap_di_campo_Analisi,
        den_app=den_apparenteAnalisi,
        stratoRadicale=strato_radici / 100., RFUperc=RFUperc)



    context= {

        'appezzamento': appez_riferimento,
        'bilancio_appezzam': bilancio_appezzam,
        'ultimo_intervento': ultimo_intervento_irriguo,
        'giorni_ciclo_colturale': giorni,
        'Ucalcolo': U,
        'Amin_irr':Airr_min,
    }

    return render(request,'singolo_appez_info.html',context)

class BilancioCreateView(BSModalCreateView):
    template_name = 'create_bilancio.html'
    form_class = BilancioForm
    success_message = 'Successo: Bilancio was created.'
    success_url = reverse_lazy('lista-appezzamenti')

class BilancioUpdateView(BSModalUpdateView):
    model = bilancio
    template_name = 'update_bilancio.html'
    form_class = BilancioForm
    success_message = 'Successo: Bilancio è stato aggiornato.'
    success_url = reverse_lazy('lista-appezzamenti')

def export_appezz(request,uid=99):
    try:
        UID = int(uid)
    except ValueError:
        raise Http404()

    appez_riferimento = appezzamentoCampo.objects.get(pk=UID)
    bilancio_appezzam = bilancio.objects.filter(appezzamentoDaCampo=uid)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    # xlsx_data = WriteToExcel(weather_period, town)
    xlsx_data = WriteToExcel(appez_riferimento, bilancio_appezzam)
    response.write(xlsx_data)
    return response

def ChartView(request,uid=2):
    appez_riferimento = appezzamento.objects.get(pk=uid)

    return render(request, "charts.html", {"uid": uid,'nome_app':appez_riferimento.nome,})

def ChartViewCampo(request,uid):
    appez_riferimento = appezzamentoCampo.objects.get(pk=uid)

    return render(request, "charts.html", {"uid": uid,'nome_app':appez_riferimento.campi.nome,})

@login_required
def get_bilancio_idrico_data(request):
    if request.method == 'GET':
        appezzamentoID = request.GET.get('appezzamentoid')
        appezzamento = appezzamentoCampo.objects.filter(id=appezzamentoID)
        if appezzamento.count() == 1:
            bilancio_appezzam = bilancio.objects.filter(appezzamentoDaCampo=appezzamento.first())[:30]
        else:
            bilancio_appezzam = bilancio.objects.none().values('data_rif','dose_antropica')

        labels = [bil.data_rif.strftime('%d/%m/%Y') for bil in bilancio_appezzam]
        dose_antropica = [bil.dose_antropica for bil in bilancio_appezzam]

        data ={
            'labels':labels,
            'dose_antropica':dose_antropica,
        }
        return JsonResponse(data)

    else:
        return Http404


def get_data(request, uid=1):
    try:
        uid = int(uid)
    except ValueError:
        raise Http404()
    bilancio_appezzam = bilancio.objects.filter(appezzamento=uid)
    labels = []
    default_items = []
    Etc = []
    A = []
    Amin_irr = []
    dose = []
    dose_antropica = []
    Ks = []
    Kc = []
    Irr_mm=[]
    for bilancio_giorno in bilancio_appezzam:
        labels.append(bilancio_giorno.data_rif.strftime('%d/%m/%Y'))
        default_items.append(bilancio_giorno.pioggia_cum)
        Etc.append(bilancio_giorno.Etc)
        A.append(bilancio_giorno.A)
        Amin_irr.append(bilancio_giorno.Amin_irr)
        dose.append(bilancio_giorno.dose)
        dose_antropica.append(bilancio_giorno.dose_antropica)
        Kc.append(bilancio_giorno.Kc)
        Ks.append(bilancio_giorno.Ks)
        Irr_mm.append(bilancio_giorno.Irr_mm)
    data = {
        "labels": labels,
        "default": default_items,
        "Etc": Etc,
        "A": A,
        "Amin_irr": Amin_irr,
        "dose": dose,
        "dose_antropica":dose_antropica,
        "Kc": Kc,
        "Ks": Ks,
        "Irr":Irr_mm,
        "users": User.objects.all().count(),
    }
    return JsonResponse(data)

def get_campi_data(request,uid=1):
    '''
    denominata api-data-campi
    :param request:
    :param uid:
    :return: json
    '''
    try:
        uid = int(uid)
    except ValueError:
        raise Http404()
    bilancio_appezzam = bilancio.objects.filter(appezzamentoDaCampo=uid)
    # prendo i dati meteo della stazione più vicina
    geometria_campo = bilancio_appezzam[0].appezzamentoDaCampo.campi.geom
    appezzam_pnt = geometria_campo.centroid
    stazione_closest = stazioni_retevista.objects.annotate(
        distance=Distance('geom', appezzam_pnt)
    ).order_by('distance').first()

    labels = []
    default_items = []
    Etc = []
    A = []
    Amin_irr = []
    dose = []
    Tmin = []
    Tmedia = []
    Tmax = []
    Ks = []
    Kc = []
    Irr_mm = []
    for bilancio_giorno in bilancio_appezzam:
        labels.append(bilancio_giorno.data_rif.strftime('%d/%m/%Y'))
        default_items.append(bilancio_giorno.pioggia_cum)
        Etc.append(bilancio_giorno.Etc)
        A.append(bilancio_giorno.A)
        Amin_irr.append(bilancio_giorno.Amin_irr)
        giorno_precedente = bilancio_giorno.data_rif-timedelta(days=1)
        dato_meteorologico = dati_aggregati_daily.objects.get(stazione=stazione_closest, data=giorno_precedente)
        Tmin.append(
            dato_meteorologico.temp_min)
        Tmedia.append(
            dato_meteorologico.temp_mean)
        Tmax.append(
            dato_meteorologico.temp_max)
        Kc.append(bilancio_giorno.Kc)
        Ks.append(bilancio_giorno.Ks)
        dose.append(bilancio_giorno.dose)
        Irr_mm.append(bilancio_giorno.Irr_mm)
    data = {
        "labels": labels,
        "default": default_items,
        "Etc": Etc,
        "A": A,
        "Amin_irr":Amin_irr,
        "Tmin": Tmin,
        "Tmedia":Tmedia,
        "Tmax":Tmax,
        "dose": dose,
        "Kc":Kc,
        "Ks":Ks,
        "Irr": Irr_mm,
        "users": User.objects.all().count(),
    }
    return JsonResponse(data)

def api_meteo_campi(request):
    if request.method == 'GET':
        campoID = request.GET.get('campo')
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')

        # campo = campi.objects.filter(id=campoID).values('nome','geom','coltura', 'data_inizio',
        #                                                 'uso_colturale', 'precocita', 'data_semina',
        #                                                 'data_raccolta', 'semente', 'produzione',
        #                                                 'irrigato', 'tessitura', 'drenaggio',
        #                                                 'gestione', 'pendenza', 'dataApportoIrriguo',
        #                                                 )
        campo = campi.objects.get(id=campoID)
        stazione_closest = stazioni_retevista.objects.annotate(
            distance=Distance('geom', campo.geom.centroid)
        ).order_by('distance').first()

        if start_date is not None and end_date is not None:
            dati_meteo_daily = dati_aggregati_daily.objects.filter(stazione=stazione_closest,data__gt=start_date,data__lte=end_date)
        else:
            dati_meteo_daily = dati_aggregati_daily.objects.filter(stazione=stazione_closest)[:30]
        # preparo la serializzazione
        Tmin = [meteo.temp_min for meteo in dati_meteo_daily]
        Tmean = [meteo.temp_mean for meteo in dati_meteo_daily]
        Tmax = [meteo.temp_max for meteo in dati_meteo_daily]
        wind = [meteo.wind_speed_mean for meteo in dati_meteo_daily]
        rain = [meteo.rain_cumulata for meteo in dati_meteo_daily]
        hum_max = [meteo.humrel_max for meteo in dati_meteo_daily]
        hum_min = [meteo.humrel_min for meteo in dati_meteo_daily]
        labels = [meteo.data.strftime('%d/%m/%Y') for meteo in dati_meteo_daily]

        data ={
            "labels": labels,
            "Tmin": Tmin,
            "Tmean": Tmean,
            "Tmax": Tmax,
            "wind": wind,
            "rain": rain,
            "hum_max": hum_max,
            "hum_min": hum_min,
            "nome": stazione_closest.nome,
        }
        return JsonResponse(data)
    else:
        return Http404


class RasterCasaDeleteView(LoginRequiredMixin,DeleteView):
    model = rasterAppezzamento
    template_name = 'confirm_delete.html'
    success_message = '''Successo: Il raster è stato correttamente eliminato.'''
    success_url = reverse_lazy('lista-fertilizzazione')

@login_required
def form_add_raster(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RasterCasaForm(request.POST,request.FILES)
        # check whether it's valid:
        if form.is_valid():
            raster = form.save(commit=False)

            # automaticamente posso fare operazioni se necessario

            raster.save()
            messages.success(request, 'Il tuo raster è stato aggiunto!')
            # redirect to a new URL:
            return redirect('lista-fertilizzazione')
    else:
        form = RasterCasaForm()
        if request.user.groups.filter(name='Agricoltori').exists():
            sel_proprietario = False
        if request.user.is_staff or request.user.groups.filter(name='Universita').exists():
            sel_proprietario = True

    return render(request, 'raster_form.html', {'form': form})

@login_required()
def raster_lista(request):
    rasterAll = rasterAppezzamento.objects.all()
    return render(request,"lista-raster-fertilizzazione.html",{
        "rasters":rasterAll,
    })

@login_required()
def raster_mappa(request,uid=1):
    try:
        uid = int(uid)
    except ValueError:
        raise Http404()


    rasterSingolo = rasterAppezzamento.objects.get(pk=uid)
    rst = GDALRaster(rasterSingolo.raster.path, write=False)
    #prendo il massimo ed il minimo dai valori del raster
    dati=rst.bands[0].data()
    massimo=dati.max()
    #filtro tutti i valori sotto-100 per non prendere i valori negativi del raster
    minimo = dati[(dati > -1000)].min()

    warning = True
    error_desc = ''
    if rst.srs.srid == 4326:
        if rst.origin[0]<18:
            warning = False
        else:
            error_desc = 'anche se il SR appare corretto  i valori non lo sono'
    else:
        error_desc = 'Il SR del raster non corrisponde a 4326'

    context = {
        "uid":uid,
        "raster":rasterSingolo.raster,
        "nome":rasterSingolo.titolo,
        "minimo":minimo,
        "massimo":massimo,
        "originx":rst.origin.x,
        "originy": rst.origin.y,
        "warning":warning,
        "errore":error_desc,
               }

    return render(request,"mappa-raster-fertilizzazione2.html",context)