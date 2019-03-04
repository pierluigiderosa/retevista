# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy

from django.http import HttpResponse,Http404
from django.shortcuts import render
from .tables import DatiOrariTable,DatiGiornalieriTable
from .filters import StazioniFilter
from django_tables2 import RequestConfig, SingleTableView

#import models
from income.models import dati_orari,dati_aggregati_daily,stazioni_retevista
# Create your views here.

def dati_orari_view(request,uid=99):
    try:
        UID = int(uid)
    except ValueError:
        raise Http404()


    if UID == 99:
        print_table = False
        nome_stazione=''
    else:
        print_table = True
        stazione_singola = stazioni_retevista.objects.filter(pk = UID)
        nome_stazione = stazione_singola[0].nome
    # vecchia soluzione
    #copio i primi 50 valori in una nuova variabile per permettere l'rdinamento della tabella
    pieceOfQuery = copy.copy(dati_orari.objects.filter(stazione=UID))
    pieceOfQuery = pieceOfQuery[:50]
    dati_orari_tutti = DatiOrariTable(pieceOfQuery)
    RequestConfig(request, paginate={'per_page': 10}).configure(dati_orari_tutti)

    #tutte le stazioni inserite nel sistema
    stazioni = stazioni_retevista.objects.all()


    return render(request, "dati_orari.html", {'table': dati_orari_tutti,'stazioni':stazioni,'print_table': print_table,'stazione_nome': nome_stazione})


def dati_giornalieri_view(request):
    dati_giornalieri_tutti = DatiGiornalieriTable(dati_aggregati_daily.objects.all())
    RequestConfig(request, paginate={'per_page': 10}).configure(dati_giornalieri_tutti)
    return render(request, "dati_giornalieri.html",{'dati_giornalieri': dati_giornalieri_tutti})


def dati_orari_list(request):
    f = StazioniFilter(request.GET, queryset=dati_orari.objects.all())
    return render(request, 'filter.html', {'filter': f})





def home_page(request):
    return render(request,"homepage.html")