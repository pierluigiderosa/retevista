# - *- coding: utf- 8 - *-

import urllib, json
from datetime import datetime, timedelta

import logging

import os

from income.models import dati_orari,stazioni_retevista


def get_and_put():
    #define log file
    logging.basicConfig(filename='data_stations.log',level=logging.DEBUG)

    #prendo le osservazioni delle ultime 3 ore
    now = datetime.now()

    earlier = now - timedelta(hours=3)

    #prendo tutte le stazioni e ottengo i dati da tutte le stazioni
    stazioni = stazioni_retevista.objects.all()

    for stazione in stazioni.iterator():
        last_3h =dati_orari.objects.filter(dataora__range=(earlier, now), stazione=stazione.id)
        UID = stazione.did
        url = 'http://api.weatherlink.com/v1/NoaaExt.json?user='+UID+'&pass=retevista01'
        response = urllib.urlopen(url)
        data = json.loads(response.read())


        # data è un dizionario che contiene il dato
        ora_oss = data['observation_time_rfc822']
        print ora_oss
        timestamp_oss = datetime.strptime(ora_oss[5:-6], '%d %b %Y %H:%M:%S')
        logging.info('ora del run:')
        logging.info(datetime.now())
        logging.info('ora osservazione:')
        logging.info(ora_oss)

        # #leggo il dato precedente
        timestamp_ora_prec = timestamp_oss - timedelta(hours=1)

        ET_day_last = 0
        ET_month_last = 0
        rain_cum_last = 0

        if last_3h:
            for osservazione in last_3h:
                if osservazione.dataora == timestamp_ora_prec:
                    rain_cum_last = osservazione.rain_cum_year
                    # se il dato riferisce la mezzanotte non leggo il valore precedente
                    if timestamp_oss.hour == 0:
                        ET_month_last = osservazione.et_cum_month
                        ET_day_last = osservazione.et_cum_day

                    else:
                        ET_day_last = osservazione.et_cum_day





        #parsing per i dati necessari
        rain_inches = data['davis_current_observation']['rain_rate_in_per_hr']
        rain_rate_mm = float(rain_inches)*25.4
        rain_cum_current = float(data['davis_current_observation']['rain_year_in'])
        rain_mm = (rain_cum_current - rain_cum_last)* 25.4
        if timestamp_oss.hour == 0:
            ET_current = float(data['davis_current_observation']['et_month'])
            ET_mm = (ET_current - ET_month_last+ET_day_last)*25.4
        else:
            ET_current = float(data['davis_current_observation']['et_day'])
            ET_mm = (ET_current - ET_day_last) * 25.4
        Celsius = data['temp_c']


        #scrivi i dati nel DB
        nuovo_dato_orario = dati_orari(
            rainrate=rain_rate_mm,
            EvapoTras=ET_mm,
            windSpeed = float(data['wind_mph'])*1.60934,
            humRel= float(data['relative_humidity']),
            pressione=float(data['pressure_mb'] ),
            solarRad=float(data['davis_current_observation']['solar_radiation']),
            dataora = timestamp_oss,
            pioggia=rain_mm,
            temp=Celsius,
            et_cum_year=float(data['davis_current_observation']['et_year']),
            et_cum_month=float(data['davis_current_observation']['et_month']),
            et_cum_day=float(data['davis_current_observation']['et_day']),
            rain_cum_year=float(data['davis_current_observation']['rain_year_in']),
            rain_cum_month=float(data['davis_current_observation']['rain_month_in']),
            rain_cum_day=float(data['davis_current_observation']['rain_day_in']),
            stazione=stazione,

        )



        if last_3h.count() > 0:
                logging.debug('ultima ora presente in DB delle ultime 3')
                logging.debug(last_3h[0].dataora)
                if last_3h[0].dataora == datetime.strptime(ora_oss[5:-6], '%d %b %Y %H:%M:%S'):
                    logging.warning('%s dato del non inserito in quanto gia presente' %(stazione.nome))



                else:
                    nuovo_dato_orario.save()
        else:
                logging.debug('no data in last 3 hours')
                nuovo_dato_orario.save()

        logging.debug(datetime.strptime(ora_oss[5:-6], '%d %b %Y %H:%M:%S'))
        logging.info('------')
