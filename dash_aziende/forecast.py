# -*- coding: utf-8 -*-

'''
modulo python per accedere ai dati di previsione meteo di ￼
openweathermap
https://openweathermap.org/current
'''

import requests
import urllib, json
from datetime import datetime as dt
from dash_aziende.models import campi


def get(latitudine=43.22,longitudine=12.433):
    API_key = 'd2dd721cd064137dada0b95db0bad273'  #api key personale
    first_url='http://api.openweathermap.org/data/2.5/weather?'

    url_complete=first_url+'lat='+latitudine.__str__()+'&lon='+longitudine.__str__()+'&APPID='+API_key+'&units=metric&lang=it'

    response = urllib.urlopen(url_complete)
    data = json.loads(response.read())
    data['trattamento'] = False
    if data['wind']['speed'] < 2.5:
        if data['main']['temp'] > 10 and data['main']['temp'] < 25:
            if data['main']['humidity'] > 50:
                data['trattamento']=True


    return data


def forecast5d(latitudine=43.22,longitudine=12.433):
    # API_key = 'd2dd721cd064137dada0b95db0bad273'  #api key personale
    # first_url='http://api.openweathermap.org/data/2.5/forecast?'
    API_keyDarsky = '231e48747e1dd1c4289165e774aa7f94'
    prima_parte='https://api.darksky.net/forecast/'

    # url_complete=first_url+'lat='+latitudine.__str__()+'&lon='+longitudine.__str__()+'&APPID='+API_key+'&units=metric&lang=it'
    url_completeDarsky = prima_parte+API_keyDarsky+'/'+str(latitudine)+','+str(longitudine)+'?units=si&lang=it&exclude=currently,flags'

    response = urllib.urlopen(url_completeDarsky)
    data = json.loads(response.read())

    return data

def save_forecast():
    #loop su tutti i campi
    for campo in campi.objects.all():
        previsione = forecast5d(longitudine=campo.geom.centroid.x,latitudine=campo.geom.centroid.y)
        campo.previsione_meteo = previsione
        campo.save()

