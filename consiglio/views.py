# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .bilancio_idrico import calc_bilancio
from django.http import HttpResponse


# Create your views here.

def show_bilancio(request):

    ieri,stazione_nome,Tmax,Tmin,RH_max,RH_min,SRmedia,vel_vento,Et0,pioggia,area,dose, A, Irr_mm = calc_bilancio()

    context = {
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
        'area': area,
        'dose': dose,
        'A': A,
        'Irr_mm': Irr_mm,
    }
    return render(request,'show_bilancio.html',context)