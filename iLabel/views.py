# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bootstrap_modal_forms.generic import BSModalCreateView
from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models import Extent
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy

from dash_aziende.models import Profile, campi, ColturaDettaglio


# Create your views here.
from iLabel.forms import PrenotazioneForm


def iLabel_main(request):
    return render(request, 'iLabel/homepageShop.html')



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

    colture = ColturaDettaglio.objects.filter(campo__proprietario=azienda)

    areaHa=[]
    produzione=[]
    for coltura in colture:
        coltura.campo.geom.transform(3004)
        area = colture.first().campo.geom.area
        area = round(area/10000.,1)
        areaHa.append(area)
        prod_tot = coltura.produzione * area
        produzione.append(prod_tot)

    bbox = campi_all.aggregate(Extent('geom'))
    colture = zip(colture,areaHa,produzione)
    return render(request,'iLabel/dash_consumatore2.html',{
        'azienda':azienda,
        'campi': campi_all,
        'colture': colture,
        'bbox': bbox['geom__extent'],
        "azienda": azienda,
    })

@login_required
def dash_list_consumatore(request):
    aziende = Profile.objects.all()

    return render(request, 'iLabel/dash_list_consumatore.html', {
        'aziende': aziende,
    })


class prenotazioneCreate(BSModalCreateView):
    template_name = 'iLabel/createPrenotazione.html'
    form_class = PrenotazioneForm
    success_message = 'Successo: La tua prenotazione è andata a buon fine'
    success_url = reverse_lazy('iLabel:main-ilabel')

    # def form_valid(self, form):
    #     if not self.request.is_ajax():
    #         app = form.save(commit=False)
    #         utente = self.request.user
    #         app.acquirente = Profile.objects.get(user=utente)
    #         # app.coltura = ColturaDettaglio.objects.first()
    #         app.save()
    #     return HttpResponseRedirect(self.success_url)

