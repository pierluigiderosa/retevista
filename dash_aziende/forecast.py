# -*- coding: utf-8 -*-

'''
modulo python per accedere ai dati di previsione meteo di ￼
openweathermap
https://openweathermap.org/current
'''

import requests
import urllib, json

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


    pass
    return data


def forecast5d(latitudine=43.22,longitudine=12.433):
    API_key = 'd2dd721cd064137dada0b95db0bad273'  #api key personale
    first_url='http://api.openweathermap.org/data/2.5/forecast?'


    url_complete=first_url+'lat='+latitudine.__str__()+'&lon='+longitudine.__str__()+'&APPID='+API_key+'&units=metric&lang=it'

    response = urllib.urlopen(url_complete)
    data = json.loads(response.read())
    return data
