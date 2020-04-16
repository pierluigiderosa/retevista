# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models import Extent
from django.http import Http404
from django.shortcuts import render

from dash_aziende.models import Profile, campi


# Create your views here.

def iLabel_main(request):
    return render(request, 'iLabel/homepage.html')



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
    return render(request,'iLabel/dash_consumatore.html',{
        'campi': campi_all,
        'bbox': bbox['geom__extent'],
        "azienda": azienda,
    })

@login_required
def dash_list_consumatore(request):
    aziende = Profile.objects.all()

    return render(request, 'iLabel/dash_list_consumatore.html', {
        'aziende': aziende,
    })
