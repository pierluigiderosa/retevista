# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .bilancio_idrico import calc_bilancio
from consiglio.models import appezzamento,bilancio
from django.http import HttpResponse


# Create your views here.

def lista_appezzamenti(request):

    lista_appez = appezzamento.objects.all()

    ieri,stazione_nome,Tmax,Tmin,RH_max,RH_min,SRmedia,vel_vento,Et0,pioggia,cap_id_zero,area,dose, A, Irr_mm = calc_bilancio()

    context = {
        'lista_appez':lista_appez,
        'ieri': ieri.strftime('%d/%m/%Y'),
        'stazione_nome': stazione_nome,
        'Tmax': Tmax,
        'Tmin': Tmin,
        'RH_max': RH_max,
        'RH_min': RH_min,
        'SRmedia': SRmedia,
        'vel_vento':vel_vento,
        'Et0':Et0,
        'pioggia': pioggia,
        'cap_id_zero': cap_id_zero,
        'area': area,
        'dose': dose,
        'A': A,
        'Irr_mm': Irr_mm,
    }
    return render(request, 'lista_appezzamenti.html', context)


def singolo_appezz(request,uid=99):

    appez_riferimento = appezzamento.objects.get(pk=1)
    bilancio_appezzam = bilancio.objects.filter(appezzamento=uid)
    soglia_intervento = appez_riferimento.cap_idrica-appez_riferimento.ris_fac_util

    context ={
        'cap_idricamax':appez_riferimento.cap_idrica,
        'bilancio_appezzam':bilancio_appezzam,
        'soglia':soglia_intervento,
    }

    return render(request,'singolo_appez.html',context)