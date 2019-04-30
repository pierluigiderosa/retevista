# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy

from .bilancio_idrico import calc_bilancio
from consiglio.models import appezzamento,bilancio
from income.models import dati_aggregati_daily
from .WriteToExcel import WriteToExcel

from .forms import BilancioForm
from bootstrap_modal_forms.generic import (
                                           BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)


# Create your views here.

def lista_appezzamenti(request):

    lista_appez = appezzamento.objects.all()

    # ieri,stazione_nome,Tmax,Tmin,RH_max,RH_min,SRmedia,vel_vento,Et0,pioggia,cap_id_zero,area,dose, A, Irr_mm = calc_bilancio()

    context = {
        'lista_appez':lista_appez,
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

def ChartView(request):
    return render(request, "charts.html", {"customers": 1010})

def get_data(request, *args, **kwargs):
    qs_count = User.objects.all().count()
    dati_giornalieri_tutti = dati_aggregati_daily.objects.filter(stazione=1)
    bilancio_appezzam = bilancio.objects.filter(appezzamento=1)
    labels = []
    default_items = []
    Etc = []
    for bilancio_giorno in bilancio_appezzam:
        labels.append(bilancio_giorno.data_rif.strftime('%d/%m/%Y'))
        default_items.append(bilancio_giorno.pioggia_cum)
        Etc.append(bilancio_giorno.Etc)
    data = {
        "labels": labels,
        "default": default_items,
        "Etc": Etc,
        "users": User.objects.all().count(),
    }
    return JsonResponse(data)