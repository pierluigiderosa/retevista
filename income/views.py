# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy

from django.core.serializers import serialize
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from djgeojson.views import GeoJSONLayerView
from pandas import read_excel

from consiglio.WriteToExcel import WriteToExcelRain

from .tables import DatiOrariTable, DatiGiornalieriTable
from .filters import StazioniFilter
from django_tables2 import RequestConfig
from datetime import date, timedelta

# import models
from income.models import dati_orari, dati_aggregati_daily, stazioni_retevista, dati_spi, stazioni_umbria


# Create your views here.

def dati_orari_view(request, uid=99):
    try:
        UID = int(uid)
    except ValueError:
        raise Http404()

    if UID == 99:
        print_table = False
        nome_stazione = ''
    else:
        print_table = True
        stazione_singola = stazioni_retevista.objects.filter(pk=UID)
        nome_stazione = stazione_singola[0].nome
    # vecchia soluzione
    # copio i primi 50 valori in una nuova variabile per permettere l'ordinamento della tabella
    pieceOfQuery = copy.copy(dati_orari.objects.filter(stazione=UID))
    pieceOfQuery = pieceOfQuery[:50]
    dati_orari_tutti = DatiOrariTable(pieceOfQuery)
    RequestConfig(request, paginate={'per_page': 10}).configure(dati_orari_tutti)

    # tutte le stazioni inserite nel sistema
    stazioni = stazioni_retevista.objects.all()

    return render(request, "dati_orari.html",
                  {'table': dati_orari_tutti, 'stazioni': stazioni, 'print_table': print_table,
                   'stazione_nome': nome_stazione})


def dati_giornalieri_view(request, uid=99):
    try:
        UID = int(uid)
    except ValueError:
        raise Http404()

    if UID == 99:
        print_table = False
        nome_stazione = ''
    else:
        print_table = True
        stazione_singola = stazioni_retevista.objects.filter(pk=UID)
        nome_stazione = stazione_singola[0].nome

    dati_giornalieri_tutti = DatiGiornalieriTable(dati_aggregati_daily.objects.filter(stazione=UID))
    # dati_giornalieri_tutti = DatiGiornalieriTable(dati_aggregati_daily.objects.all())
    RequestConfig(request, paginate={'per_page': 15}).configure(dati_giornalieri_tutti)

    # tutte le stazioni inserite nel sistema
    stazioni = stazioni_retevista.objects.all()

    return render(request, "dati_giornalieri.html", {
        'dati_giornalieri': dati_giornalieri_tutti,
        'stazioni': stazioni, 'print_table': print_table, 'stazione_nome': nome_stazione,
        'app_id': UID,
    })


def dati_orari_list(request):
    f = StazioniFilter(request.GET, queryset=dati_orari.objects.all())
    return render(request, 'filter.html', {'filter': f})


# def points_view():#request):
#     data = []
#     stazioni= stazioni_retevista.objects.all()
#     for stazione in stazioni:
#         dati_meteo = dati_aggregati_daily.objects.filter(stazione=stazione).first()
#         stazione_meteo = list(chain(stazione, dati_meteo))
#         data.append(stazione_meteo)
#     points_as_geojson = serialize('geojson', stazioni)
#     return points_as_geojson
#     # return HttpResponse(points_as_geojson, content_type='json')


class points_view(GeoJSONLayerView):
    # Options
    precision = 4  # float
    simplify = 0.5  # generalization
    geom = 'geom'  # colonna geometrie
    properties = ['nome', 'did']

    def get_queryset(self):
        pk_id = self.request.GET.get('pid')
        try:
            pk_id_int = int(pk_id)
        except ValueError:
            Http404
        if pk_id_int == 100:
            context = stazioni_retevista.objects.all()
        else:
            # reverse selection di catastale a partire dal danno
            context = stazioni_retevista.objects.filter(id=pk_id_int)
        return context


class MapAppezz(GeoJSONLayerView):
    # Options
    precision = 4  # float
    simplify = 0.5  # generalization
    geom = 'geom'  # colonna geometrie
    properties = ['nome', ]


def mappa(request):
    rain_ieri = dati_aggregati_daily.objects.filter(data=date.today() - timedelta(days=1)).values('rain_cumulata')
    return render(request, "mappa.html")


def export_dati_daily(request, uid=99):
    try:
        UID = int(uid)
    except ValueError:
        raise Http404()

    dati_giornalieri_tutti = dati_aggregati_daily.objects.filter(stazione=UID)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    # xlsx_data = WriteToExcel(weather_period, town)
    xlsx_data = WriteToExcelRain(dati_giornalieri_tutti)
    response.write(xlsx_data)
    return response


def home_page(request):
    return render(request, "homepage.html")




def lista_stazioni_umbria_spi(request):
    stazioni_spi = stazioni_umbria.objects.filter(dati_spi__isnull=False)
    context = {
        'lista_staz_spi': stazioni_spi,
    }
    return render(request, "lista-stazioni-spi.html", context)


def get_spi(request, uid=1):
    try:
        uid = int(uid)
    except ValueError:
        raise Http404()
    staz_id = uid
    spi = dati_spi.objects.filter(stazione_pluviometrica__id=staz_id)
    if spi.count() == 1:
        spi = spi.first()
    elif spi.count() > 1:
        pass
    else:
        pass

    df = read_excel(spi.spi, sheet_name=0, header=1, skiprows=0)
    date = []
    spi_values = []

    for i in df.index:
        date.append(df[df.columns[0]][i].strftime('%m %Y'))
        spi_values.append(round(df[df.columns[1]][i],2))

    data_dict = {
        "mesianni": date,
        "spi": spi_values,

    }
    return JsonResponse(data_dict)


def ChartView(request, uid=2):
    stazione_umbria = dati_spi.objects.get(stazione_pluviometrica_id=uid)

    return render(request, "charts_spi.html", {
        "uid": uid,
        'nome_staz': stazione_umbria.stazione_pluviometrica.name,
        'spi_1mese': stazione_umbria.spi_1mesi,
        'spi_3mese': stazione_umbria.spi_3mesi,
        'spi_6mese': stazione_umbria.spi_6mesi,
        'mese':stazione_umbria.data_spi_cruscotti
    })
