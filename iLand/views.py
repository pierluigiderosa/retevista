# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.core.serializers import serialize
from django.shortcuts import render

from django.contrib.gis.db.models import Q

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from djgeojson.views import GeoJSONLayerView

from dash_aziende.models import campi, Profile
from django.contrib.gis.db.models import Extent

#reportLab -- PDF
from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse

from iLand import importer
from iLand.forms import ImportShapefileForm
from iLand.models import Shapefile, Feature, AttributeValue
from iLand.reports import report_singolo_platypus


@login_required
def homepage_iLand(request):
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

    return render(request, "iLand/main_iland.html", {
        'bbox': bbox['geom__extent'],
        'staff':staff,
    })

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

    return render(request,'iLand/main_biotopo.html',{
        'bbox': bbox['geom__extent'],
        'staff': staff,
    })


@login_required()
def catastino(request):
    return render(request,'iLand/catastino.html')


@login_required()
def list_shapefiles(request):
    shapefiles = Shapefile.objects.all().order_by("filename")
    return render(request, "iLand/list_shapefiles.html",
                  {'shapefiles': shapefiles})


@login_required()
def import_shapefile(request):
    if request.method == "GET":
        form = ImportShapefileForm()
        return render(request, "iLand/import_shapefile.html",
                      {'form'
                       : form,
                       'err_msg': None})
    elif request.method == "POST":
        form = ImportShapefileForm(request.POST,
                                   request.FILES)

        if form.is_valid():
            shapefile = request.FILES['import_file']
            encoding = request.POST['character_encoding']
            epsg = request.POST['epsg']
            tipologia = request.POST['tipologia']

            err_msg = importer.import_data(shapefile,
                                           encoding,
                                           epsg,
                                           tipologia)

            if err_msg == None:
                return render(request,"homepage.html")
        else:
            err_msg = None



        return render(request, "iLand/import_shapefile.html",
                      {'form'   : form,
                       'err_msg' : err_msg})



def ricerca(request):
    if request.method == 'GET':
        foglio = request.GET.get('foglio', '')
        particella = request.GET.get('particella', '')
        comune = request.GET.get('comune', '')
        # toglier quando analizziamo altre aziende Appolloni
        foglio_results = Feature.objects.filter(
            Q(shapefile__filename__istartswith='Appol')&
            Q(attributevalue__value__icontains=foglio) &
            Q(attributevalue__attribute__name__exact='FOGLIO')).distinct()
        particella_results = Feature.objects.filter(
            Q(shapefile__filename__istartswith='Appol') &
            Q(attributevalue__value__icontains=particella) &
            Q(attributevalue__attribute__name__contains='PARTICELLA')
        ).distinct()
        comune_results = Feature.objects.filter(
            Q(shapefile__filename__istartswith='Appol') &
            Q(attributevalue__value__icontains=comune) &
            Q(attributevalue__attribute__name__contains='COMUNE')
        ).distinct()
        search_results = foglio_results & particella_results & comune_results
        output =[]
        for elemento in search_results:
            dict={'id':elemento.id}
             #appendo id feature
            attributi = elemento.attributevalue_set.all()
            for elem in attributi:
                if elem.attribute.name == 'PARTICELLA':
                    dict['particella'] = elem.value
                elif elem.attribute.name == 'FOGLIO':
                    dict['foglio']= elem.value
                elif elem.attribute.name == 'COMUNE_1':
                    dict['comune'] = elem.value
            output.append(dict)

        return JsonResponse({'lista':list(output),'conteggio':len(search_results)},safe=False)

@login_required()
def report_vincoli(request):
    vincoli = Shapefile.objects.filter(tipologia='vincoli')
    return render(request,'iLand/report.html',{'vincoli':vincoli})


@csrf_exempt
def vincoli_pdf(request):
    if request.method == 'GET':
        lista = request.GET.get('features')

        featureIDS = lista.split(',')
        featureIDS.remove('')

        pdf = report_singolo_platypus(catastale='Appol',lista_feature=featureIDS) #todo : Appol da togliere quando metteremo altre aziende

        return pdf

    else:
        return Http404
