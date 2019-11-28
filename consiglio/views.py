# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, JsonResponse

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django_common.mixin import LoginRequiredMixin

from consiglio.models import appezzamento,bilancio,appezzamentoCampo,rasterAppezzamento
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

    lista_appez = appezzamento.objects.all()
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
    for appezzamentoNew in lista_appezCampo:
        if appezzamentoNew.campi.analisi_suolo_set.exists():
            analisi = appezzamentoNew.campi.analisi_suolo_set.first()
            cap_di_campo_Analisi = analisi.cap_di_campo
            punto_appassimentoAnalisi =analisi.punto_appassimento
            den_apparenteAnalisi = analisi.den_apparente
        else:
            cap_di_campo_Analisi = appezzamentoNew.cap_di_campo
            punto_appassimentoAnalisi = appezzamentoNew.punto_appassimento
            den_apparenteAnalisi = appezzamentoNew.den_app
        strato_radici = appezzamentoNew.strato_radici
        RFUperc = appezzamentoNew.perc_riserva_util
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
        'lista_appez':lista_appez,
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

def singolo_appezz_campo(request,uid=99):
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

    appez_riferimento = appezzamento.objects.get(pk=UID)
    bilancio_appezzam = bilancio.objects.filter(appezzamento=uid)

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
    dose = []
    for bilancio_giorno in bilancio_appezzam:
        labels.append(bilancio_giorno.data_rif.strftime('%d/%m/%Y'))
        default_items.append(bilancio_giorno.pioggia_cum)
        Etc.append(bilancio_giorno.Etc)
        A.append(bilancio_giorno.A)
        dose.append(bilancio_giorno.dose)
    data = {
        "labels": labels,
        "default": default_items,
        "Etc": Etc,
        "A": A,
        "dose": dose,
        "users": User.objects.all().count(),
    }
    return JsonResponse(data)

def get_campi_data(request,uid=1):
    try:
        uid = int(uid)
    except ValueError:
        raise Http404()
    bilancio_appezzam = bilancio.objects.filter(appezzamentoDaCampo=uid)
    labels = []
    default_items = []
    Etc = []
    A = []
    dose = []
    for bilancio_giorno in bilancio_appezzam:
        labels.append(bilancio_giorno.data_rif.strftime('%d/%m/%Y'))
        default_items.append(bilancio_giorno.pioggia_cum)
        Etc.append(bilancio_giorno.Etc)
        A.append(bilancio_giorno.A)
        dose.append(bilancio_giorno.dose)
    data = {
        "labels": labels,
        "default": default_items,
        "Etc": Etc,
        "A": A,
        "dose": dose,
        "users": User.objects.all().count(),
    }
    return JsonResponse(data)

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

            # automaticamente possp fare operazioni se necessario

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


def raster_lista(request):
    rasterAll = rasterAppezzamento.objects.all()
    return render(request,"lista-raster-fertilizzazione.html",{
        "rasters":rasterAll,
    })


def raster_mappa(request,uid=1):
    try:
        uid = int(uid)
    except ValueError:
        raise Http404()


    rasterSingolo = rasterAppezzamento.objects.get(pk=uid)
    rst = GDALRaster(rasterSingolo.raster.path, write=False)
    context = {
        "uid":uid,
        "raster":rasterSingolo.raster,
        "nome":rasterSingolo.titolo,
        "originx":rst.origin.x,
        "originy": rst.origin.y,
               }

    return render(request,"mappa-raster-fertilizzazione.html",context)