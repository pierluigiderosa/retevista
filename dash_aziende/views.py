# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime,timedelta
import json

from bootstrap_modal_forms.generic import BSModalUpdateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.gis.db.models.functions import Distance
from django.core import serializers
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView, DeleteView
from djgeojson.views import GeoJSONLayerView

from django.contrib.gis.db.models import Extent, Union,Sum,Avg

from dash_aziende.models import campi, Profile, analisi_suolo, macchinari, Trasporto, ColturaDettaglio, Magazzino, \
    operazioni_colturali, analisi_prodotto, dataset_fitofarmaci, dataset_malattie, dataset_infestante, irrigazione
from income.models import dati_orari, stazioni_retevista,iframe_stazioni
from consiglio.models import bilancio,appezzamentoCampo
from dash_aziende.models import fertilizzazione as fert_model ,operazioni_colturali as oper_model,\
    irrigazione as irr_model, trattamento as tratt_model, semina as semina_model,raccolta as raccolta_model, \
    raccolta_paglia as raccolta_paglia_model, diserbo as diserbo_model

from .forms import CampiAziendeForm, UserForm, ProfileForm, AnalisiForm, \
    FertilizzazioneForm, OperazioneColturaleForm, IrrigazioneForm, TrattamentoForm, SeminaForm, \
    RaccoltaForm, \
    EditProfileForm, MacchinariForm, TrasportiForm, ColturaDettaglioForm, RaccoltaPagliaForm, DiserboForm, \
    MagazzinoForm, MacchinariFormAgricoltore, AnalisiProdottiForm
from forecast import get as get_forecast

# Create your views here.
from .report_dash_aziende import report_macchinari, report_analisi, report_quaderno


@login_required
def dashboard_main(request):
    utente = request.user
    campi_all = None
    if utente.groups.filter(name='Agricoltori').exists():
        campi_all = campi.objects.filter(proprietario=Profile.objects.filter(user=utente))
        staff = False
    elif utente.is_staff or utente.groups.filter(name='Universita').exists():
        campi_all = campi.objects.all()
        staff = True
    else:
        campi_all = campi.objects.none()
    latlong = []
    bbox = campi_all.aggregate(Extent('geom'))

    return render(request, "main_iland.html", {
        'bbox': bbox['geom__extent'],
        'staff':staff,
    })

@login_required
def main_ifarm(request):
    utente = request.user
    if utente.groups.filter(name='Agricoltori').exists():
        campi_all = campi.objects.filter(proprietario=Profile.objects.filter(user=utente))
        staff = False
    elif utente.is_staff or utente.groups.filter(name='Universita').exists():
        campi_all = campi.objects.all()
        staff = True
    else:
        campi_all = campi.objects.none()
    bbox = campi_all.aggregate(Extent('geom'))
    areeHa = []
    campi3004 = campi_all.transform(3004, field_name='geom')
    for campo in campi3004:
        areeHa.append(round(campo.geom.area/10000.,1)) #calcolo area in ha

    zipped = zip(campi_all,areeHa)

    return render(request, "main_ifarm.html", {
        'campi': zipped,
        'staff':staff,
    })

@login_required
def elenco_quaderni(request):
    utente = request.user
    if utente.groups.filter(name='Agricoltori').exists():
        campi_all = campi.objects.filter(proprietario=Profile.objects.filter(user=utente))
        staff = False
    elif utente.is_staff or utente.groups.filter(name='Universita').exists():
        campi_all = campi.objects.all()
        staff = True
    else:
        campi_all = campi.objects.none()
    return render(request,'elenco_quaderni.html',{'campi':campi_all})

@login_required
def print_quaderno(request,pk):
    utente = request.user
    try:
        UID = int(pk)
    except ValueError:
        raise Http404()

    if utente.groups.filter(name='Agricoltori').exists():
        azienda = Profile.objects.filter(user=utente)
        campo = campi.objects.get(id=UID)
        operazioni_all =operazioni_colturali.objects.filter(campo=campo)
    elif utente.is_staff or utente.groups.filter(name='Universita').exists():
        azienda = Profile.objects.none()
        campo = campi.objects.get(id=UID)
        operazioni_all = operazioni_colturali.objects.filter(campo=campo)
    else:
        operazioni_all = operazioni_colturali.objects.none()
        azienda = Profile.objects.none()

    pdfQuaderno = report_quaderno(operazioni_all,azienda)

    return pdfQuaderno

@login_required
def main_iFoodPrint(request):
    utente = request.user
    if utente.groups.filter(name='Agricoltori').exists():
        campi_all = campi.objects.filter(proprietario=Profile.objects.filter(user=utente))
        staff = False
        Coltivazioni =ColturaDettaglio.objects.filter(campo__in=campi_all)
    elif utente.is_staff or utente.groups.filter(name='Universita').exists():
        campi_all = campi.objects.all()
        staff = True
        Coltivazioni =ColturaDettaglio.objects.filter(campo__in=campi_all)
    else:
        campi_all = campi.objects.none()
        Coltivazioni =ColturaDettaglio.objects.filter(campo__in=campi_all)
    bbox = campi_all.aggregate(Extent('geom'))

    return render(request, "main_iFoodPrint.html", {
        'bbox': bbox['geom__extent'],
        'staff':staff,
        'Coltivazioni': Coltivazioni,
        'campi': campi_all,
    })

@login_required
def iFoodPrint_detail(request, uid):
    utente = request.user
    try:
        UID = int(uid)
    except ValueError:
        raise Http404()
    campo = campi.objects.get(id=UID)
    analisi_all = analisi_suolo.objects.filter(campo=campo)
    centroide = campo.geom.centroid
    campo.geom.transform(3004)
    areaHa = campo.geom.area/10000.
    if campo.colturadettaglio_set.exists():
        coltivazione = campo.colturadettaglio_set.first()

        # estraggo la CO2 totale
        CO2info = dict()
        CO2_operazioni = operazioni_colturali.objects.filter(coltura_dettaglio=coltivazione).values(
            'CO2operazione').aggregate(
            CO2tot=Sum('CO2operazione'))
        CO2tot = CO2_operazioni['CO2tot']
        if CO2tot is None:
            CO2tot = 0
            CO2info['operazioni'] = 0
        else:
            CO2info['operazioni'] = CO2_operazioni['CO2tot']

        if coltivazione.trasporto_set.exists():
            CO2trasporto = Trasporto.objects.filter(coltura=coltivazione).values('CO2_trasporto').aggregate(
                CO2tot=Sum('CO2_trasporto'))
            CO2tot += CO2trasporto['CO2tot']
            CO2info['trasporto'] = CO2trasporto['CO2tot']
            trasporto = Trasporto.objects.filter(coltura=coltivazione)
        else:
            trasporto = Trasporto.objects.none()


        # estrazione dati per calcolo azoto, fosforo
        operazioni = operazioni_colturali.objects.filter(coltura_dettaglio=coltivazione, operazione='fertilizzazione')


        totN = 0
        totP=0
        totK=0

        for i in range(len(operazioni)):
            if operazioni[i].operazione_fertilizzazione is not None:
                Ndistribuita = operazioni[i].operazione_fertilizzazione.titolo_n
                fosforo = operazioni[i].operazione_fertilizzazione.titolo_p2o5
                potassio = operazioni[i].operazione_fertilizzazione.titolo_k2o
                KgProdottoTot = operazioni[i].operazione_fertilizzazione.kg_prodotto
                totN = totN + (Ndistribuita/100. * KgProdottoTot)
                totP = totP + (fosforo/100. * KgProdottoTot)
                totK = totK + (potassio/100. * KgProdottoTot)

        # si divive per 1000 oper passare a Ton
        NdistribuitaTot = round(totN * areaHa / 1000.,2)
        PdistribuitaTot = round(totP * areaHa / 1000.,2)
        KdistribuitaTot = round(totK * areaHa / 1000.,2)

        prodotti = analisi_prodotto.objects.filter(prodotto=coltivazione)

    else:
        coltivazione = ColturaDettaglio.objects.none()
        trasporto = Trasporto.objects.none()
        prodotti = analisi_prodotto.objects.none()

    # estrazione dati per calcolo H2O utilizzata
    irrigazioni = irrigazione.objects.filter(operazioni_colturali__coltura_dettaglio=coltivazione).values(
        'portata').aggregate(totH20=Sum('portata'))


    # controllo se è presente il dato di casadei
    appezzamentoID = None
    if campo.appezzamentocampo_set.exists():
        appezzamento =appezzamentoCampo.objects.filter(campi=campo)
    #     prendo il primo ma ora su ogni campo posso mettere un solo appezzamento
        appezzamento = appezzamento.first()
        appezzamentoID = appezzamento.id



    return render(request, 'iFoodPrint2-dettaglio.html', {
        'campo':campo,
        'areaHa':areaHa,
        'CO2': int(CO2tot / 1000.),
        'CO2info': CO2info,
        'Ndistibuita': NdistribuitaTot,
        'Pdistibuita': PdistribuitaTot,
        'Kdistibuita': KdistribuitaTot,
        'acqua': irrigazioni['totH20'],
        'appezzamentoID': appezzamentoID,
        'analisi':analisi_all,
        'analisi_prodotto':prodotti.first(), # todo: prendo solo un analisi prodotto
        'centroide':centroide,
        'coltivazione':coltivazione,
        'produzione':round(coltivazione.produzione * areaHa,1),
        'trasporti':trasporto,
    })

@login_required
def iFoodPrint_panel(request,uid):
    try:
        UID = int(uid)
    except ValueError:
        raise Http404()
    campo = campi.objects.get(id=UID)
    if campo.colturadettaglio_set.exists():
        coltivazione = campo.colturadettaglio_set.first()
        # estraggo la CO2 totale
        CO2info = dict()
        CO2_operazioni = operazioni_colturali.objects.filter(coltura_dettaglio=coltivazione).values('CO2operazione').aggregate(
            CO2tot=Sum('CO2operazione'))
        CO2tot = CO2_operazioni['CO2tot']
        if CO2tot is None:
            CO2tot=0
            CO2info['operazioni'] = 0
        else:
            CO2info['operazioni']=CO2_operazioni['CO2tot']
        if coltivazione.trasporto_set.exists():
            CO2trasporto = Trasporto.objects.filter(coltura=coltivazione).values('CO2_trasporto').aggregate(
                CO2tot=Sum('CO2_trasporto'))
            CO2tot += CO2trasporto['CO2tot']
            CO2info['trasporto'] = CO2trasporto['CO2tot']
            trasporto = Trasporto.objects.filter(coltura=coltivazione)
        else:
            trasporto = Trasporto.objects.none()

        # estrazione dati per calcolo azoto
        operazioni= operazioni_colturali.objects.filter(coltura_dettaglio=coltivazione, operazione='fertilizzazione')

        tot=0
        for i in range(len(operazioni)):
            if operazioni[i].operazione_fertilizzazione is not None:
                Ndistribuita = operazioni[i].operazione_fertilizzazione.titolo_n
                KgProdottoTot = operazioni[i].operazione_fertilizzazione.kg_prodotto
                tot = tot+(Ndistribuita*KgProdottoTot)

        campo.geom.transform(3004)
        areaHa = campo.geom.area / 10000.
        NdistribuitaTot= int(tot*areaHa/1000)


    else:
        coltivazione = ColturaDettaglio.objects.none()
        trasporto = Trasporto.objects.none()


    return render(request,'iFoodPrin_panel.html',{
        'campo':campo,
        'CO2':int(CO2tot/1000.),
        'CO2info':CO2info,
        'Ndistibuita': NdistribuitaTot,
        'coltivazione':coltivazione,
    })

@login_required
def dashboard_fields(request,forecast=False):
    utente = request.user
    if utente.groups.filter(name='Agricoltori').exists():
        campi_all =  campi.objects.filter(proprietario=Profile.objects.filter(user=utente))
        staff = False
    if utente.is_staff or utente.groups.filter(name='Universita').exists():
        campi_all = campi.objects.all()
        staff=True
    latlong = []
    bbox = campi_all.aggregate(Extent('geom'))
    forecast_data = []
    iframeURL=[]
    for campo in campi_all:
        latlong.append([campo.geom.centroid.x,campo.geom.centroid.y])
        stazione_closest = stazioni_retevista.objects.annotate(
                distance=Distance('geom', campo.geom)
            ).order_by('distance').first()
        iframeURLsingolo=iframe_stazioni.objects.get(stazioni=stazione_closest)
        iframeURL.append(iframeURLsingolo.iframeURL)
        if forecast:
            forecast_single = get_forecast(campo.geom.centroid.y,campo.geom.centroid.x)
            forecast_data.append(forecast_single)

        else:
            forecast_data.append(None)
    areeHa = []
    campi3004 = campi_all.transform(3004, field_name='geom')
    for campo in campi3004:
        areeHa.append(round(campo.geom.area / 10000., 1)) #calcolo area in Ha
    zipped = zip(campi_all, areeHa, latlong, forecast_data, iframeURL)



    return render(request, "dashboard.html", {
        'campi':zipped,
        'staff': staff,
        'bbox': bbox['geom__extent'],
        'forecast': forecast,
                                              })

@login_required
def dashboard_consiglio(request):
    utente = request.user
    campi_all = None
    if utente.groups.filter(name='Agricoltori').exists():
        campi_all = campi.objects.filter(proprietario=Profile.objects.filter(user=utente))
        staff = False
    elif utente.is_staff or utente.groups.filter(name='Universita').exists():
        campi_all = campi.objects.all()
        staff = True
    else:
        campi_all = campi.objects.none()

    appezzamentoCampo.objects.filter(campi=campi_all)
    appezzamenti = appezzamentoCampo.objects.filter(campi__in=campi_all)
    areeKm2 = []
    dati_meteorologici = []
    bilanci =[]
    extent_campi = []
    # appezzamenti3004 = appezzamenti.transform(3004, field_name='geom')
    for app_singolo in appezzamenti:
        extent_campi.append(app_singolo.campi.geom.extent)
        app_singolo.campi.geom.transform(3004)
        areeKm2.append(round(app_singolo.campi.geom.area / 10000., 1))  # calcolo area in ha
        #prendo i dati della stazione meteo più vicina
        stazione_closest = stazioni_retevista.objects.annotate(
            distance=Distance('geom', app_singolo.campi.geom)
        ).order_by('distance').first()
        dati_orari_prossimi = dati_orari.objects.filter(stazione=stazione_closest).first()
        dati_meteorologici.append(
            {'EtCorrente': float(dati_orari_prossimi.et_cum_day) * 25.4,
            'TCorrente': float(dati_orari_prossimi.temp),
            'UmRelCorrente': float(dati_orari_prossimi.humRel),
            'WindCorrente': float(dati_orari_prossimi.windSpeed)}
        )
        #prendo i dati del bilancio corrispondente ad appezzamento
        bilanci.append( bilancio.objects.filter(appezzamentoDaCampo=app_singolo).first() )



    bbox = campi_all.aggregate(Extent('geom'))
    zipped=zip(appezzamenti,areeKm2,dati_meteorologici,bilanci,extent_campi)

    return render(request, "dashboard_consiglio.html", {
        'bbox': bbox['geom__extent'],
        'appezzamenti': zipped,
        'staff': staff,
    })

@login_required
def dash_operazioni_colturali(request):
    utente = request.user
    oper_all = None
    if utente.groups.filter(name='Agricoltori').exists():
        oper_all = oper_model.objects.filter(campo__proprietario=Profile.objects.filter(user=utente))
        staff = False
    elif utente.is_staff or utente.groups.filter(name='Universita').exists():
        oper_all = oper_model.objects.all()
        staff = True
    else:
        oper_all = oper_model.objects.none()


    tipologia_operazioni = oper_model.operazione_choices
    bbox = oper_all.aggregate(Extent('campo__geom'))
    return render(request,"operazioni_dashboard.html",{
        "tipologia_operazioni": tipologia_operazioni,
        "operazioni_all": oper_all,
        "bbox": bbox['campo__geom__extent'],
        'staff': staff,
    })

@login_required
def dashboard_analisi(request):
    utente = request.user
    if utente.groups.filter(name='Agricoltori').exists():
        campi_all = campi.objects.filter(proprietario=Profile.objects.filter(user=utente))
        staff = False
    if utente.is_staff or utente.groups.filter(name='Universita').exists():
        campi_all = campi.objects.all()
        staff = True
    # campi_all = campi.objects.filter(proprietario=Profile.objects.filter(user=request.user))
    analisi_all = analisi_suolo.objects.filter(campo__in=campi_all)

    # aggrego i valori medi per ogni campo
    aggregati=[]
    for campo in campi_all:

        el_analisi = analisi_suolo.objects.filter(campo=campo).aggregate(Avg('sabbia'), Avg('limo'), Avg('argilla'),
                                                                         Avg('pH'), Avg('conduttivita_elettrica'),
                                                                         Avg('OM'), Avg('azoto'), Avg('Carbonio'),
                                                                         Avg('fosforo'),Avg('potassio'),
                                                                         Avg('scambio_cationico'),Avg('CACO3_tot'),
                                                                         Avg('CACO3_att'),Avg('den_apparente'),
                                                                         Avg('pietrosita'),Avg('profondita'),
                                                                         Avg('cap_di_campo'),Avg('punto_appassimento'))
        el_analisi['denominazione']=campo.nome
        el_analisi['pk']=campo.id
        aggregati.append(el_analisi)



    bbox_condition = True
    if analisi_all.count() == 1:
        bbox_condition = False
    bbox = campi_all.aggregate(Extent('geom'))


    return render(request,'analisi_dashboard.html',
                  {
                      'analisies':analisi_all,
                      'staff': staff,
                      'aggregati':aggregati,
                      'bbox': bbox['geom__extent'],
                      'bbox_condition': bbox_condition,
                  })

@login_required
def analisi_report_pdf(request,pk):
    try:
        UID = int(pk)
    except ValueError:
        raise Http404()

    pdf = report_analisi(UID)
    return pdf

#inizio delle view per i consumatori
@login_required
def dash_consumatore(request,uid=-9999):
    try:
        UID = int(uid)
    except ValueError:
        raise Http404()
    if uid==-9999:
        azienda = Profile.objects.get(id=15)
    else:
        azienda = Profile.objects.get(id=uid)


    campi_all = campi.objects.filter(proprietario=azienda)

    bbox = campi_all.aggregate(Extent('geom'))
    return render(request,'dash_consumatore.html',{
        'campi': campi_all,
        'bbox': bbox['geom__extent'],
        "azienda": azienda,
    })


@login_required
def list_macchinari(request,uid=-9999):
    utente = request.user

    if utente.groups.filter(name='Agricoltori').exists():
        macchinari_all = macchinari.objects.filter(azienda=Profile.objects.filter(user=utente))
        azienda = Profile.objects.filter(user=utente)
    elif utente.is_staff or utente.groups.filter(name='Universita').exists():
        macchinari_all = macchinari.objects.all()
        azienda = Profile.objects.none()
    else:
        macchinari_all = macchinari.objects.none()
        azienda = Profile.objects.none()


    return render(request,'macchinari.html',{
        'macchinari': macchinari_all,
        "azienda": azienda
    })

@csrf_exempt
def macchinari_pdf(request):
    utente = request.user

    if utente.groups.filter(name='Agricoltori').exists():
        macchinari_all = macchinari.objects.filter(azienda=Profile.objects.filter(user=utente))
        azienda = Profile.objects.filter(user=utente)
    elif utente.is_staff or utente.groups.filter(name='Universita').exists():
        macchinari_all = macchinari.objects.all()
        azienda = Profile.objects.none()
    else:
        macchinari_all = macchinari.objects.none()
        azienda = Profile.objects.none()

    pdf = report_macchinari(macchinari_all,azienda)

    return pdf


@login_required
def logistica_list(request):
    utente = request.user
    if utente.groups.filter(name='Agricoltori').exists():
        azienda = Profile.objects.filter(user=utente)
        trasporti = Trasporto.objects.filter(coltura__campo__proprietario=azienda)
    elif utente.is_staff or utente.groups.filter(name='Universita').exists():
        azienda = Profile.objects.none()
        trasporti = Trasporto.objects.all()
    else:
        azienda = Profile.objects.none()
        trasporti = Trasporto.objects.none()

    return render(request, 'logistica.html', {
        'trasporti': trasporti,
        "azienda": azienda
    })


@login_required
def magazzini_list(request):
    utente = request.user
    if utente.groups.filter(name='Agricoltori').exists():
        magazzini_all = Magazzino.objects.filter(azienda=Profile.objects.filter(user=utente))
        azienda = Profile.objects.filter(user=utente)
    elif utente.is_staff or utente.groups.filter(name='Universita').exists():
        magazzini_all = Magazzino.objects.all()
        azienda = Profile.objects.none()
    else:
        magazzini_all = Magazzino.objects.none()
        azienda = Profile.objects.none()

    return render(request, 'magazzini.html', {
        'magazzini': magazzini_all,
        "azienda": azienda
    })

@login_required
def analisi_prodotti(request):
    utente = request.user
    if utente.groups.filter(name='Agricoltori').exists():
        azienda = Profile.objects.filter(user=utente)
        analisi_prodotti= analisi_prodotto.objects.filter(prodotto__campo__proprietario=azienda)

    elif utente.is_staff or utente.groups.filter(name='Universita').exists():
        azienda = Profile.objects.none()
        analisi_prodotti = analisi_prodotto.objects.all()
    else:
        azienda = Profile.objects.none()
        analisi_prodotti = analisi_prodotto.objects.none()

    return render(request,'analisi_prodotto.html',{
        'analisi':analisi_prodotti,
        'azienda':azienda,
    })

@login_required
def analisi_prodotti_Add(request):
    if request.method == 'POST':
        form = AnalisiProdottiForm(request.POST)
        if form.is_valid():
            analisi_prodotti = form.save(commit=False)
            analisi_prodotti.save()
            messages.success(request, 'la tua analisi prodotta è stata aggiunta!')
            return redirect('analisi-prodotti')
    else:
        form = AnalisiProdottiForm()
    return render(request,'analisi_prodotto_add.html',{'form':form})

@login_required
def main_biotipo(request):
    utente = request.user
    if utente.groups.filter(name='Agricoltori').exists():
        campi_all = campi.objects.filter(proprietario=Profile.objects.filter(user=utente))
        staff = False
    elif utente.is_staff or utente.groups.filter(name='Universita').exists():
        campi_all = campi.objects.all()
        staff = True
    else:
        campi_all = campi.objects.none()
    bbox = campi_all.aggregate(Extent('geom'))

    return render(request,'main_biotopo.html',{
        'bbox': bbox['geom__extent'],
        'staff': staff,
    })

@login_required
def dash_list_consumatore(request):
    aziende = Profile.objects.all()

    return render(request, 'dash_list_consumatore.html', {
        'aziende': aziende,
    })


#inizio delle views per i forms ----
@login_required
def form_campi(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CampiAziendeForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            campo = form.save(commit=False)

            # automaticamente assegno il proprietario del campo
            if request.user.groups.filter(name='Agricoltori').exists():
                campo.proprietario = Profile.objects.get(user=request.user)

            campo.save()
            # process the data in form.cleaned_data as required
            # ...
            messages.success(request, 'Il tuo campo è stato aggiunto!')
            # redirect to a new URL:
            return redirect('main-fields')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CampiAziendeForm()
        if request.user.groups.filter(name='Agricoltori').exists():
            sel_proprietario = False
        if request.user.is_staff or request.user.groups.filter(name='Universita').exists():
            sel_proprietario = True

    return render(request, 'dashboard_form.html', {'form': form, 'proprietario': sel_proprietario})

@login_required
def form_coltura(request):
    if request.method == 'POST':
        form = ColturaDettaglioForm(request.POST)
        if form.is_valid():
            coltura = form.save(commit=False)

             # automaticamente assegno qualcosa se serve
            coltura.save()
            messages.success(request,'La coltura è stata aggiunta')
            return redirect('main-fields')
    else:
        form = ColturaDettaglioForm()
        if request.user.groups.filter(name='Agricoltori').exists():
            sel_proprietario = False
            campi_all = campi.objects.filter(proprietario=Profile.objects.filter(user=request.user))
            form.fields['campo'].queryset = campi_all
        if request.user.is_staff or request.user.groups.filter(name='Universita').exists():
            sel_proprietario = True

    return render(request, 'coltivazione_form.html', {'form': form})


@login_required
def form_macchinari(request):
    if request.method == 'POST':
        if request.user.groups.filter(name='Agricoltori').exists():
            form = MacchinariFormAgricoltore(request.POST,request.FILES)
            if form.is_valid():
                macchinario = form.save(commit=False)
                # automaticamente assegno il proprietario del campo
                macchinario.azienda = Profile.objects.get(user=request.user)
                macchinario.save()
                messages.success(request, 'Il tuo macchinario è stato aggiunto!')
                # redirect to a new URL:
                return redirect('lista-macchinari')

        if request.user.is_staff or request.user.groups.filter(name='Universita').exists():
            form = MacchinariForm(request.POST,request.FILES)
            if form.is_valid():
                macchinario = form.save(commit=False)

                macchinario.save()
                # process the data in form.cleaned_data as required
                # ...
                messages.success(request, 'Il tuo macchinario è stato aggiunto!')
                # redirect to a new URL:
                return redirect('lista-macchinari')

                # if a GET (or any other method) we'll create a blank form
    else:
        if request.user.groups.filter(name='Agricoltori').exists():
            sel_proprietario = False
            form = MacchinariFormAgricoltore()
        if request.user.is_staff or request.user.groups.filter(name='Universita').exists():
            sel_proprietario = True
            form = MacchinariForm()

    return render(request, 'macchinari_form.html', {'form': form, 'proprietario': sel_proprietario})


@login_required
def form_logistica_add(request):
    if request.method == 'POST':
        form = TrasportiForm(request.POST)
        if form.is_valid():
            logistica = form.save(commit=False)

            # automaticamente assegno qualcosa qui
            # if request.user.groups.filter(name='Agricoltori').exists():
            #     macchinario.azienda = Profile.objects.get(user=request.user)

            logistica.save()
            # process the data in form.cleaned_data as required
            # ...
            messages.success(request, 'Il tuo trasporto è stato aggiunto!')
            # redirect to a new URL:
            return redirect('lista_logistica')

            # if a GET (or any other method) we'll create a blank form
    else:
        form = TrasportiForm()
        if request.user.groups.filter(name='Agricoltori').exists():
            sel_proprietario = False
        if request.user.is_staff or request.user.groups.filter(name='Universita').exists():
            sel_proprietario = True

    return render(request, 'logistica_form.html', {'form': form, 'proprietario': sel_proprietario})

@login_required
def form_magazzino_add(request):
    if request.method == 'POST':
        form = MagazzinoForm(request.POST)
        if form.is_valid():
            magazzino = form.save(commit=False)

            # automaticamente assegno qualcosa qui
            # if request.user.groups.filter(name='Agricoltori').exists():
            #     macchinario.azienda = Profile.objects.get(user=request.user)

            magazzino.save()
            # process the data in form.cleaned_data as required
            # ...
            messages.success(request, 'Il tuo magazzino è stato aggiunto!')
            # redirect to a new URL:
            return redirect('lista_logistica')

            # if a GET (or any other method) we'll create a blank form
    else:
        form = MagazzinoForm()
        if request.user.groups.filter(name='Agricoltori').exists():
            sel_proprietario = False
        if request.user.is_staff or request.user.groups.filter(name='Universita').exists():
            sel_proprietario = True

    return render(request, 'magazzino_form.html', {'form': form, 'proprietario': sel_proprietario})

@login_required
def form_operazioni(request,oper_type=None):
    '''This function creates a brand new fertilizzazione object with related Book objects using inlineformset_factory'''
    utente = request.user
    if utente.groups.filter(name='Agricoltori').exists():
        query_campi_utente = campi.objects.filter(proprietario=Profile.objects.filter(user=request.user))
        colturadettaglioFilter = ColturaDettaglio.objects.filter(campo__in=query_campi_utente)
        staff = False
    if utente.is_staff or utente.groups.filter(name='Universita').exists():
        query_campi_utente = campi.objects.all()
        colturadettaglioFilter = ColturaDettaglio.objects.all()
        staff = True

    #caso fertilizzazione
    if oper_type=='fertilizzazione':
        child_operation = fert_model()
        child_form = FertilizzazioneForm(instance=child_operation)  # setup a form for the parent


        OperationFormSet = inlineformset_factory(
            fert_model, oper_model,
            form=OperazioneColturaleForm,
            fields='__all__',
            fk_name='operazione_fertilizzazione',
            can_delete=False,
            extra=1,
        )

        if request.method == "POST":
            child_form = FertilizzazioneForm(request.POST,instance=child_operation)
            formset = OperationFormSet(request.POST, request.FILES,instance=child_operation)


            if child_form.is_valid():
                created_fertilizzazione = child_form.save(commit=False)
                formset = OperationFormSet(request.POST, request.FILES, instance=created_fertilizzazione)
                OperazioneColturaleForm.operazione=oper_type

                if formset.is_valid():
                    created_fertilizzazione.save()
                    operazioni = formset.save(commit=False)

                    for single_oper in operazioni:
                        single_oper.operazione=oper_type
                        single_oper.campo = single_oper.coltura_dettaglio.campo
                        single_oper.save()

                messages.success(request, 'la tua fertilizzazione è stata aggiunta!')
                # redirect to a new URL:
                return redirect('main-operazioni-colturali')

        else:
            child_form = FertilizzazioneForm(instance=child_operation)

            formset = OperationFormSet(instance=child_operation)
            for form in formset.forms:
                form.fields['coltura_dettaglio'].queryset = colturadettaglioFilter
                # form.fields['campo'].queryset = query_campi_utente
    
    #caso irrigazione
    elif oper_type=='irrigazione':
        child_operation = irr_model()  #cambiare qui
        child_form = IrrigazioneForm(instance=child_operation)  # setup a form for the parent CAMBIARE QUI

        OperationFormSet = inlineformset_factory(
            irr_model, oper_model,   #CAMBIARE QUI
            form=OperazioneColturaleForm,
            fields='__all__',
            fk_name='operazione_irrigazione',  #CAMBIARE QUI
            can_delete=False, 
            extra=1,
        )

        if request.method == "POST":
            child_form = IrrigazioneForm(request.POST,instance=child_operation)  #CAMBIARE QUI
            formset = OperationFormSet(request.POST, request.FILES,instance=child_operation)

            if child_form.is_valid():
                created_fertilizzazione = child_form.save(commit=False)
                created_fertilizzazione.operazione = oper_type
                formset = OperationFormSet(request.POST, request.FILES, instance=created_fertilizzazione)

                if formset.is_valid():
                    created_fertilizzazione.save()
                    operazioni = formset.save(commit=False)

                    for single_oper in operazioni:
                        single_oper.operazione=oper_type
                        single_oper.campo = single_oper.coltura_dettaglio.campo
                        single_oper.save()

                messages.success(request, 'la tua irrigazione è stata aggiunta!')
                # redirect to a new URL:
                return redirect('main-operazioni-colturali')
        else:
            child_form = IrrigazioneForm(instance=child_operation) #CAMBIARE QUI
            formset = OperationFormSet(instance=child_operation)
            for form in formset.forms:
                form.fields['coltura_dettaglio'].queryset = colturadettaglioFilter
                # form.fields['campo'].queryset = query_campi_utente

    #caso trattamento
    elif oper_type=='trattamento':
        child_operation = tratt_model()  #cambiare qui
        child_form = TrattamentoForm(instance=child_operation)  # setup a form for the parent CAMBIARE QUI

        OperationFormSet = inlineformset_factory(
            tratt_model, oper_model,   #CAMBIARE QUI
            form=OperazioneColturaleForm,
            fields='__all__',
            fk_name='operazione_trattamento',  #CAMBIARE QUI
            can_delete=False,
            extra=1,
        )

        if request.method == "POST":
            child_form = TrattamentoForm(request.POST,instance=child_operation)  #CAMBIARE QUI
            formset = OperationFormSet(request.POST, request.FILES,instance=child_operation)

            if child_form.is_valid():
                created_fertilizzazione = child_form.save(commit=False)
                created_fertilizzazione.operazione = oper_type
                formset = OperationFormSet(request.POST, request.FILES, instance=created_fertilizzazione)

                if formset.is_valid():
                    created_fertilizzazione.save()
                    operazioni = formset.save(commit=False)

                    for single_oper in operazioni:
                        single_oper.operazione=oper_type
                        single_oper.campo = single_oper.coltura_dettaglio.campo
                        single_oper.save()

                messages.success(request, 'il tuo trattamento è stato aggiunto!')
                # redirect to a new URL:
                return redirect('main-operazioni-colturali')
        else:
            child_form = TrattamentoForm(instance=child_operation) #CAMBIARE QUI
            formset = OperationFormSet(instance=child_operation)
            for form in formset.forms:
                form.fields['coltura_dettaglio'].queryset = colturadettaglioFilter
                # form.fields['campo'].queryset = query_campi_utente

    #caso semina
    elif oper_type=='semina_trapianto':
        child_operation = semina_model()  #cambiare qui
        child_form = SeminaForm(instance=child_operation)  # setup a form for the parent CAMBIARE QUI

        OperationFormSet = inlineformset_factory(
            semina_model, oper_model,   #CAMBIARE QUI
            form=OperazioneColturaleForm,
            fields='__all__',
            fk_name='operazione_semina',  #CAMBIARE QUI
            can_delete=False,
            extra=1,
        )

        if request.method == "POST":
            child_form = SeminaForm(request.POST,instance=child_operation)  #CAMBIARE QUI
            formset = OperationFormSet(request.POST, request.FILES,instance=child_operation)

            if child_form.is_valid():
                created_fertilizzazione = child_form.save(commit=False)
                created_fertilizzazione.operazione = oper_type
                formset = OperationFormSet(request.POST, request.FILES, instance=created_fertilizzazione)

                if formset.is_valid():
                    created_fertilizzazione.save()
                    operazioni = formset.save(commit=False)

                    for single_oper in operazioni:
                        single_oper.operazione=oper_type
                        single_oper.campo = single_oper.coltura_dettaglio.campo
                        single_oper.save()

                messages.success(request, 'la tua semina è stata aggiunta!')
                # redirect to a new URL:
                return redirect('main-operazioni-colturali')
        else:
            child_form = SeminaForm(instance=child_operation) #CAMBIARE QUI
            formset = OperationFormSet(instance=child_operation)
            for form in formset.forms:
                form.fields['coltura_dettaglio'].queryset = colturadettaglioFilter
                # form.fields['campo'].queryset = query_campi_utente

    #caso raccolta
    elif oper_type=='raccolta':
        child_operation = raccolta_model()  #cambiare qui
        child_form = RaccoltaForm(instance=child_operation)  # setup a form for the parent CAMBIARE QUI

        OperationFormSet = inlineformset_factory(
            raccolta_model, oper_model,   #CAMBIARE QUI
            form=OperazioneColturaleForm,
            fields='__all__',
            fk_name='operazione_raccolta',  #CAMBIARE QUI
            can_delete=False,
            extra=1,
        )

        if request.method == "POST":
            child_form = RaccoltaForm(request.POST,instance=child_operation)  #CAMBIARE QUI
            formset = OperationFormSet(request.POST, request.FILES,instance=child_operation)

            if child_form.is_valid():
                created_fertilizzazione = child_form.save(commit=False)
                created_fertilizzazione.operazione = oper_type
                formset = OperationFormSet(request.POST, request.FILES, instance=created_fertilizzazione)

                if formset.is_valid():
                    created_fertilizzazione.save()
                    operazioni = formset.save(commit=False)

                    for single_oper in operazioni:
                        single_oper.operazione=oper_type
                        single_oper.campo = single_oper.coltura_dettaglio.campo
                        single_oper.save()

                messages.success(request, 'la tua raccolta è stata aggiunta!')
                # redirect to a new URL:
                return redirect('main-operazioni-colturali')
        else:
            child_form = RaccoltaForm(instance=child_operation) #CAMBIARE QUI
            formset = OperationFormSet(instance=child_operation)
            for form in formset.forms:
                form.fields['coltura_dettaglio'].queryset = colturadettaglioFilter
                # form.fields['campo'].queryset = query_campi_utente

    # caso raccolta paglia
    elif oper_type=='raccolta_paglia':
        child_operation = raccolta_paglia_model()  #cambiare qui
        child_form = RaccoltaPagliaForm(instance=child_operation)  # setup a form for the parent CAMBIARE QUI

        OperationFormSet = inlineformset_factory(
            raccolta_paglia_model, oper_model,   #CAMBIARE QUI
            form=OperazioneColturaleForm,
            fields='__all__',
            fk_name='operazione_raccolta_paglia',  #CAMBIARE QUI
            can_delete=False,
            extra=1,
        )

        if request.method == "POST":
            child_form = RaccoltaPagliaForm(request.POST,instance=child_operation)  #CAMBIARE QUI
            formset = OperationFormSet(request.POST, request.FILES,instance=child_operation)

            if child_form.is_valid():
                created_fertilizzazione = child_form.save(commit=False)
                created_fertilizzazione.operazione = oper_type
                formset = OperationFormSet(request.POST, request.FILES, instance=created_fertilizzazione)

                if formset.is_valid():
                    created_fertilizzazione.save()
                    operazioni = formset.save(commit=False)

                    for single_oper in operazioni:
                        single_oper.operazione=oper_type
                        single_oper.campo = single_oper.coltura_dettaglio.campo
                        single_oper.save()

                messages.success(request, 'la tua raccolta di paglia è stata aggiunta!')
                # redirect to a new URL:
                return redirect('main-operazioni-colturali')


        else:
            child_form = RaccoltaPagliaForm(instance=child_operation) #CAMBIARE QUI
            formset = OperationFormSet(instance=child_operation)
            for form in formset.forms:
                form.fields['coltura_dettaglio'].queryset = colturadettaglioFilter
                # form.fields['campo'].queryset = query_campi_utente

    # caso diserbo
    elif oper_type == 'diserbo':
        child_operation = diserbo_model()  # cambiare qui
        child_form = DiserboForm(instance=child_operation)  # setup a form for the parent CAMBIARE QUI

        OperationFormSet = inlineformset_factory(
            diserbo_model, oper_model,  # CAMBIARE QUI
            form=OperazioneColturaleForm,
            fields='__all__',
            fk_name='operazione_diserbo',  # CAMBIARE QUI
            can_delete=False,
            extra=1,
        )

        if request.method == "POST":
            child_form = DiserboForm(request.POST, instance=child_operation)  # CAMBIARE QUI
            formset = OperationFormSet(request.POST, request.FILES, instance=child_operation)

            if child_form.is_valid():
                created_fertilizzazione = child_form.save(commit=False)
                created_fertilizzazione.operazione = oper_type
                formset = OperationFormSet(request.POST, request.FILES, instance=created_fertilizzazione)

                if formset.is_valid():
                    created_fertilizzazione.save()
                    operazioni = formset.save(commit=False)

                    for single_oper in operazioni:
                        single_oper.operazione = oper_type
                        single_oper.campo = single_oper.coltura_dettaglio.campo
                        single_oper.save()

                messages.success(request, 'il tuo diserbo è stato aggiunto!')
                # redirect to a new URL:
                return redirect('main-operazioni-colturali')


        else:
            child_form = DiserboForm(instance=child_operation)  # CAMBIARE QUI
            formset = OperationFormSet(instance=child_operation)
            for form in formset.forms:
                form.fields['coltura_dettaglio'].queryset = colturadettaglioFilter
                # form.fields['campo'].queryset = query_campi_utente


    # casi solo data
    elif oper_type=='aratura':
        if request.method == 'POST':
            form = OperazioneColturaleForm(request.POST)
            if form.is_valid():
                operazioni = form.save(commit=False)
                operazioni.operazione= oper_type
                operazioni.campo=operazioni.coltura_dettaglio.campo
                operazioni.save()

            messages.success(request,'La aratura è stata aggiunta')
            return redirect('main-operazioni-colturali')
        else:
            formset = OperazioneColturaleForm()
            child_form = None

    elif oper_type=='estirpatura':
        if request.method == 'POST':
            form = OperazioneColturaleForm(request.POST)
            if form.is_valid():
                operazioni = form.save(commit=False)
                operazioni.operazione= oper_type
                operazioni.campo=operazioni.coltura_dettaglio.campo
                operazioni.save()

            messages.success(request,'La estirpatura è stata aggiunta')
            return redirect('main-operazioni-colturali')
        else:
            formset = OperazioneColturaleForm()
            child_form = None

    elif oper_type=='erpicatura':
        if request.method == 'POST':
            form = OperazioneColturaleForm(request.POST)
            if form.is_valid():
                operazioni = form.save(commit=False)
                operazioni.operazione= oper_type
                operazioni.campo=operazioni.coltura_dettaglio.campo
                operazioni.save()

            messages.success(request,'La erpicatura è stata aggiunta')
            return redirect('main-operazioni-colturali')
        else:
            formset = OperazioneColturaleForm()
            child_form = None

    elif oper_type=='rullatura':
        if request.method == 'POST':
            form = OperazioneColturaleForm(request.POST)
            if form.is_valid():
                operazioni = form.save(commit=False)
                operazioni.operazione= oper_type
                operazioni.campo=operazioni.coltura_dettaglio.campo
                operazioni.save()

            messages.success(request,'La rullatura è stata aggiunta')
            return redirect('main-operazioni-colturali')
        else:
            formset = OperazioneColturaleForm()
            child_form = None

    else:
        child_form=None
        formset=None
        oper_type=oper_type+' non ancora inserita. Contatta il gestore del sito'

    return render(request,"operazioni_form.html",{
        "child_form": child_form,
        "formset_operazione": formset,
        "titolo_child":oper_type,
    })



@login_required
def form_analisi(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AnalisiForm(request.user, request.POST)
        # check whether it's valid:
        if form.is_valid():
            analisi = form.save(commit=False)
            # process the data in form.cleaned_data as required
            # ...

            analisi.save()

            messages.success(request, 'la tua analisi è stata aggiunta!')
            # redirect to a new URL:
            return redirect('main-analisi')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AnalisiForm(request.user)

    return render(request, 'analisi_form.html', {'form': form})

@login_required
def autocomplete_fitofarmaci(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        search_qs = dataset_fitofarmaci.objects.filter(FORMULATO__istartswith=q)[:15]
        results = []
        print q
        for r in search_qs:
            results.append(r.FORMULATO+' | '+r.PRODUTTORE+' | '+r.SOSTANZA_ATTIVA_PER_100G_DI_PRODOTTO+' |  '+r.SOSTANZE_ATTIVE)
            # results.append({"value":r.FORMULATO,"data":r.PRODUTTORE+' | '+r.SOSTANZA_ATTIVA_PER_100G_DI_PRODOTTO+' |  '+r.SOSTANZE_ATTIVE})
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

@login_required
def autocomplete_malattie(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        search_qs = dataset_malattie.objects.filter(malattia__istartswith=q)
        results = []
        print q
        for r in search_qs:
            results.append(r.malattia+' gruppo:'+r.gruppo)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

@login_required
def autocomplete_erbe(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        search_qs = dataset_infestante.objects.filter(infestante__istartswith=q)
        results = []
        print q
        for r in search_qs:
            results.append(r.infestante+' gruppo:'+r.gruppo)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

@login_required
def get_operazioni_data(request):
    if request.method == 'GET':
        colturaID = request.GET.get('colturaid')
        start_date=request.GET.get('start')
        end_date=request.GET.get('end')
        start_date=datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        delta = timedelta(days=1)
        colturaRif = ColturaDettaglio.objects.get(id=colturaID)
        trattamenti=[]
        fertilizzazioni=[]
        # queste due variabili conservano i valori totali da esportare come json

        if colturaRif.operazioni_colturali_set.exists():
            operations = operazioni_colturali.objects.filter(coltura_dettaglio=colturaRif)
            for operazione in operations:
                if operazione.operazione == 'trattamento':
                    trattamenti.append(operazione.data_operazione)
                elif operazione.operazione == 'fertilizzazione':
                    fertilizzazioni.append(operazione.data_operazione)

        trattamentiList = []
        fertilizzazioniList = []
        labels=[]
        # inizio a fare un ciclo tra data inizioe e fine per fare timeseries
        start_dateWhile = start_date
        while start_dateWhile <= end_date:
            # popolo i trattamenti
            if start_dateWhile in trattamenti:
                trattamentiList.append(100)
            else:
                trattamentiList.append(0)

            # popolo le fertilizzazioni
            if start_dateWhile in fertilizzazioni:
                fertilizzazioniList.append(100)
            else:
                fertilizzazioniList.append(0)

            labels.append(start_dateWhile.strftime('%d/%m/%Y'))
            #incremento di un giorno
            start_dateWhile += delta

        return JsonResponse(
            {
                'labels':labels,
                'trattamenti': trattamentiList,
             'fertilizzazioni':fertilizzazioniList,
             })
    else:
        mimetype = 'application/json'
        return HttpResponse('fail', mimetype)


class CampoUpdateView(LoginRequiredMixin,UpdateView):
    model = campi
    template_name = 'dashboard_form.html'
    form_class = CampiAziendeForm
    success_message = 'Successo: Il campo è stato aggiornato.'
    success_url = reverse_lazy('main-fields')
    # fields = '__all__'


class ColtivazioneDeleteView(LoginRequiredMixin,DeleteView):
    model = ColturaDettaglio
    template_name = 'confirm_delete.html'
    success_message = 'Successo: la coltura sul campo è stata eliminata.'
    success_url = reverse_lazy('main-fields')

class CampoDeleteView(LoginRequiredMixin,DeleteView):
    model = campi
    template_name = 'confirm_delete.html'
    success_message = 'Successo: Il campo è stato eliminato.'
    success_url = reverse_lazy('main-fields')

class AnalisiUpdateView(LoginRequiredMixin,UpdateView):
    model = analisi_suolo
    template_name = 'analisi_form.html'
    form_class = AnalisiForm
    success_message = "Successo: L'analisi è stata aggiornato."
    success_url = reverse_lazy('main-analisi')

    def get_form_kwargs(self):
        """This method is what injects forms with their keyword
            arguments."""
        # grab the current set of form #kwargs
        kwargs = super(AnalisiUpdateView, self).get_form_kwargs()
        # Update the kwargs with the user_id
        kwargs['user'] = self.request.user
        return kwargs

class MacchinariUpdateView(LoginRequiredMixin,UpdateView):
    model = macchinari
    template_name = 'macchinari_form_edit.html'
    form_class = MacchinariFormAgricoltore
    # fields = '__all__'
    success_message = "Successo: Il macchinario è stato aggiornato."
    success_url = reverse_lazy('lista-macchinari')





class AnalisiDeleteView(LoginRequiredMixin,DeleteView):
    model = analisi_suolo
    template_name = 'confirm_delete.html'
    success_message = '''Successo: L'analisi è stato eliminato.'''
    success_url = reverse_lazy('main-analisi')

class MacchinariDeleteView(LoginRequiredMixin,DeleteView):
    model = macchinari
    template_name = 'confirm_delete.html'
    success_message = '''Successo: Il macchinario è stato eliminato.'''
    success_url = reverse_lazy('lista-macchinari')

class OperazioniDeleteView(LoginRequiredMixin,DeleteView):
    model = oper_model
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('main-operazioni-colturali')
    success_message = '''Successo: L'operazione è stata eliminata.'''


@login_required()
def get_data_charts(request):
    campi_all = campi.objects.filter(proprietario=Profile.objects.filter(user=request.user))
    campi_coltura_aggregati = campi_all.values('coltura__nome').annotate(Union('geom')).transform(3004)

    coltura = []
    area = []
    for campo_coltura in campi_coltura_aggregati:
        coltura.append(campo_coltura['coltura__nome'])
        area.append(round(campo_coltura['geom__union'].area/10000.,3))
    data = {
        "labels": coltura,
        "default": area,
    }
    return JsonResponse(data)




@login_required()
@transaction.atomic
def add_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            # process the data in form.cleaned_data as required
            user = user_form.save()

            user.refresh_from_db()  # This will load the Agricoltore Profile created by the Signal
            profile_form = ProfileForm(request.POST,
                                           instance=user.profile)  # Reload the profile form with the profile instance
            profile_form.full_clean()  # Manually clean the form this time. It is implicitly called by "is_valid()" method
            profile_form.save(commit=False)
            user_form.save()
            profile_form.save()  # Gracefully save the form
            grouppoAgricoltori = Group.objects.get(name='Agricoltori')
            user.groups.add(grouppoAgricoltori)
            messages.success(request, 'Il tuo profilo è stato creato!')
            # redirect to a new URL:
            return redirect('homepage')

        else:
            messages.error(request, 'Per favore correggi gli errori sotto.')
    else:
        user_form = UserForm()
        profile_form = ProfileForm()
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@login_required()
def edit_profile(request):
    editing_profile = False
    if Profile.objects.filter(user=request.user).exists():
        editing_profile = True

        if request.method == 'POST':
            form = EditProfileForm(request.POST, instance=request.user)
            profile_form = ProfileForm(request.POST, request.FILES,
                                       instance=request.user.profile)  # request.FILES is show the selected image or file

            if form.is_valid() and profile_form.is_valid():
                user_form = form.save()
                custom_form = profile_form.save(False)
                custom_form.user = user_form
                custom_form.save()
                messages.success(request, 'Il tuo profilo è stato aggiornato!')

                return redirect('homepage')
        else:
            form = EditProfileForm(instance=request.user)
            profile_form = ProfileForm(instance=request.user.profile)
            # args = {}
            # # args.update(csrf(request))
            # args['form'] = form
            # args['profile_form'] = profile_form
        return render(request, 'profile.html', {
            'user_form': form,
            'profile_form': profile_form,
            'edit_profile': editing_profile,
        })
    else:
        messages.warning(request,'Non si appartiene al gruppo degli agricoltori')
        return render(request,'profile.html',{
            'editing_profile': editing_profile,
        })

#chiamate per json
def CampiEstesiJson(request):
    #todo aggiungere and request.is_ajax()
    if request.method == 'GET':
        campoID = request.GET.get('campo')

        campo=campi.objects.filter(id=campoID).values('nome','coltura','data_inizio',
                                                      'uso_colturale','precocita','data_semina',
                                                      'data_raccolta','semente','produzione',
                                                      'irrigato','tessitura','drenaggio',
                                                      'gestione','pendenza','dataApportoIrriguo',
                                                      )
        operazioni = oper_model.objects.filter(campo=campi.objects.get(id=campoID)).values(
            'operazione','data_operazione','operazione_fertilizzazione','operazione_irrigazione',
            'operazione_raccolta','operazione_trattamento','operazione_semina','id'
        )

        data_dict = {'campo':list(campo),'n_operazioni':len(operazioni)}
        for id_operazione in range(len(operazioni)):
            data_dict['operazione'+str(id_operazione)]=operazioni[id_operazione]

        return JsonResponse(data_dict, safe=False)
    else:
        return Http404

def AnalisiJson(request):
    if request.method == "GET":
        campoID = request.GET.get('campo')
        analisi_all=analisi_suolo.objects.filter(campo__id=campoID).values(
            'data_segnalazione','id_campione','sabbia','limo','argilla','pH',
            'conduttivita_elettrica','OM','azoto','fosforo','potassio','scambio_cationico',
            'CACO3_att','CACO3_tot','den_apparente','pietrosita','profondita',
        )
        response = {'totale': analisi_all.count(),
                    'analisi':list(analisi_all)}
        return JsonResponse(response,safe=False)
    else:
        return Http404

def operazioniJson(request):
    if request.method == 'GET':
        operazioneID = request.GET.get('operazione')
        # operazioneID=8 # todo debug -- togli la riga
        operazione = oper_model.objects.get(id=operazioneID)
        operazioneDict = {}
        if operazione.operazione_fertilizzazione is not None:
            dettaglio_operazione = fert_model.objects.filter(id = operazione.operazione_fertilizzazione.id ).values(
                'fertilizzante','kg_prodotto','titolo_p2o5','titolo_n','titolo_k2o'
            )
            for field in dettaglio_operazione.first().keys():
                nome_esteso = fert_model._meta.get_field(field).verbose_name
                valore = dettaglio_operazione.first()[field]
                operazioneDict[nome_esteso]=valore
        if operazione.operazione_irrigazione is not None:
            dettaglio_operazione = irr_model.objects.filter(id = operazione.operazione_irrigazione.id ).values(
                'portata','durata',
            )
            for field in dettaglio_operazione.first().keys():
                nome_esteso = irr_model._meta.get_field(field).verbose_name
                valore = dettaglio_operazione.first()[field]
                operazioneDict[nome_esteso]=valore
        if operazione.operazione_raccolta is not None:
            dettaglio_operazione = raccolta_model.objects.filter(id=operazione.operazione_raccolta.id).values(
                'produzione',
            )
            for field in dettaglio_operazione.first().keys():
                nome_esteso = raccolta_model._meta.get_field(field).verbose_name
                valore = dettaglio_operazione.first()[field]
                operazioneDict[nome_esteso]=valore

        if operazione.operazione_trattamento is not None:
            dettaglio_operazione = tratt_model.objects.filter(id=operazione.operazione_trattamento.id).values(
                'prodotto','formulato','sostanze','quantita',
            )
            for field in dettaglio_operazione.first().keys():
                nome_esteso = tratt_model._meta.get_field(field).verbose_name
                valore = dettaglio_operazione.first()[field]
                operazioneDict[nome_esteso] = valore

        if operazione.operazione_semina is not None:
            dettaglio_operazione = semina_model.objects.filter(id=operazione.operazione_semina.id).values(
                'semina', 'quantita','precocita','lunghezza_ciclo','produzione',
            )
            for field in dettaglio_operazione.first().keys():
                nome_esteso = semina_model._meta.get_field(field).verbose_name
                valore = dettaglio_operazione.first()[field]
                operazioneDict[nome_esteso] = valore

        return JsonResponse(operazioneDict,safe=False)
    else:
        return Http404



class CampiGeoJson(GeoJSONLayerView):
    # Options
    precision = 4  # float
    simplify = None  # generalization
    geom = 'geom'  # colonna geometrie
    properties = ['nome','coltura', 'id']

    def get_queryset(self):
        userStaff = self.request.GET.get('user')
        if 'campo' in self.request.GET:
            campoID = self.request.GET.get('campo')
            context = campi.objects.filter(id=campoID)
            return context

        if userStaff == 'staff':
            context = campi.objects.all()
        else:
            context = campi.objects.filter(proprietario=Profile.objects.get(user=self.request.user))
        return context

