from .models import dati_aggregati_daily,stazioni_retevista,dati_orari
from django_pandas.io import read_frame
from datetime import timedelta, time

import datetime as dt

def aggrega():

    '''
    DATI CHE SERVONO
    #pioggia cumulata giornaliera
    #Temp min max media giornaliera
    #HumRel min e max giornaliera
    #SolarRad media giornaliera
    #Wind Speed media giornaliera
    '''

    #estraggo i dati del giorno precedente
    #inizio periodo - giorni prima di oggi
    ieri = dt.date.today() - timedelta(days=1)

    #in debug
    inizio = dt.datetime.combine(ieri,time.min)
    fine = dt.datetime.combine(ieri,time.max)
    qs = dati_orari.objects.filter(dataora__range=(inizio,fine))
    #calcolo del cumulato sulla base dei dati gia presenti in db
    ore23  = dt.datetime.strptime('2300','%H%M').time()
    ore23dt = dt.datetime.combine(ieri,ore23)
    for osservazione in qs:
        if osservazione.dataora == inizio:
            rain_inizio = osservazione.rain_cum_year
        if osservazione.dataora == ore23dt:
            rain_fine = osservazione.rain_cum_year

    #trasformo la chiamata in pandas dataframe
    df = read_frame(qs)

    #creo una nuova colonna
    df['day'] = df.dataora.apply(dt.date.strftime, args=('%Y.%m.%d',))
    print 'Conteggio elementi: '+str(df.id.count())

    #estraggo i dati di un giorno
    aa=df.loc[df['day'] == ieri]

    if df.id.count()> 0:
        pioggia_cumulata = df.groupby(['day','stazione'])['pioggia'].sum().unstack()

        temperatura_max = df.groupby(['day', 'stazione'])['temp'].max().unstack()
        temperatura_min = df.groupby(['day', 'stazione'])['temp'].min().unstack()
        temperatura_mean = df.groupby(['day', 'stazione'])['temp'].mean().unstack()

        umid_real_max = df.groupby(['day', 'stazione'])['humRel'].max().unstack()
        umid_real_min = df.groupby(['day', 'stazione'])['humRel'].min().unstack()

        solar_rad = df.groupby(['day', 'stazione'])['solarRad'].mean().unstack()

        wind_speed = df.groupby(['day', 'stazione'])['windSpeed'].mean().unstack()

        #salvo i dati nel DB uno per ogni stazione presente in DB
        stazioni = stazioni_retevista.objects.all()
        i=0
        for stazione in stazioni.iterator():

            if stazione.id != 8: #TODO ho escluso la stazione di val di rose che non manda i dati
                nuovo_dato_giornliero = dati_aggregati_daily(
                    rain_cumulata=pioggia_cumulata[stazione.nome].values.__float__(),
                    temp_min = temperatura_min[stazione.nome].values.__float__(),
                    temp_max = temperatura_max[stazione.nome].values.__float__(),
                    temp_mean = temperatura_mean[stazione.nome].values.__float__(),
                    humrel_min = umid_real_min[stazione.nome].values.__float__(),
                    humrel_max = umid_real_max[stazione.nome].values.__float__(),
                    solar_rad_mean = solar_rad[stazione.nome].values.__float__(),
                    wind_speed_mean = wind_speed[stazione.nome].values.__float__(),
                    stazione = stazione,
                    data = inizio,
                )
                i+=1

                #controllo che il dato non sia presente per nons ovrascrivere
                if dati_aggregati_daily.objects.filter(data=inizio,stazione=stazione).count()== 0:
                    nuovo_dato_giornliero.save()



