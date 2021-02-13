# -*- coding: utf-8 -*-
from datetime import datetime,date
coltura={
        "barbabietola":0,
        "favino":1,
        "frumento tenero":2,
        "girasole":3,
        "mais":4,
        "orzo":5,

    }
def get_potassio(colt):

    potassio = {'produzione': [
        0.020,
        0.023,
        0.012,
        0.018,
        0.007,
        0.040,
    ], 'residui': [
        0.030,
        0.014,
        0.010,
        0.033,
        0.014,
        0.012,
    ],
        'harvest':[
            0.8,
            0.4,
            0.4,
            0.4,
            0.5,
            0.4,
        ]
    }
    if coltura.has_key(colt):
        idx = coltura[colt]
        concent = potassio['produzione'][idx]
        residui = potassio['residui'][idx]
        harvest = potassio['harvest'][idx]
        return concent,residui,harvest
    else:
        return "Errore coltura"

def get_lisciviazione(prec):
    lisc = 0.0
    if prec <= 250:
        lisc = 0
    elif prec > 250 and prec <= 300:
        lisc=16.7
    elif prec>300 and prec <=350:
        lisc=37.5
    elif prec >350 and prec <= 400:
        lisc =50.
    elif prec > 400 and prec <= 450:
        lisc = 58.3
    elif prec > 450 and prec <= 500:
        lisc = 64.3
    elif prec >500 and prec <= 550:
        lisc = 68.8
    elif prec > 500 and prec<= 600:
        lisc = 72.2
    elif prec > 600 and prec <= 650:
        lisc = 75.
    elif prec > 650 and prec <=700:
        lisc = 77.3
    elif prec > 700 and prec <= 750:
        lisc = 79.2
    elif prec > 750 and prec <= 800:
        lisc = 80.8
    elif prec > 800 and prec <= 850:
        lisc = 82.1
    elif prec > 850 and prec <= 900:
        lisc = 83.3
    elif prec > 900 and prec <= 950:
        lisc = 84.4
    elif prec > 950 and prec <= 1000:
        lisc = 85.3
    else:
        lisc=86.1
    return  lisc




def concimazioneK(produzioneAttesa=3.5,
                  dataSemina=date(year=2019,month=04,day=15),
                  dataRaccolta=date(year=2019,month=12,day=15),
                  precipitazioni = 470.,
                  coltura='favino',
                  quantitaColturaPrec = 10.,
                  concKprecedente = 7.,
                  argilla = 10.,
                  potassioScambiabile = 1,
                  ):

    stagionemesi = abs(dataRaccolta.month - dataSemina.month)

    concentrazione, residui, harvest = get_potassio(coltura)

    # contenuto di Potassio
    contenutoK1 = (produzioneAttesa*concentrazione)*1000
    quantitaProdotta = (produzioneAttesa/harvest)-produzioneAttesa
    contenutoK2 = (quantitaProdotta*residui)*1000
    quantitaProdottaRadici = (produzioneAttesa+quantitaProdotta)*0.15
    contenutoK3 = (residui*quantitaProdottaRadici)*1000
    fabbisognoColturale = contenutoK1+contenutoK2+contenutoK3
    print fabbisognoColturale

#     K residui coltura precedente
    potassioPrecedente = quantitaColturaPrec*concKprecedente
    print potassioPrecedente

    # K lisciviazione
    potassioSolubile = (-0.2667*argilla)+0.0767
    potassioLisciviabile = potassioScambiabile*potassioSolubile
    lisciviazione = get_lisciviazione(precipitazioni)
    potassioLisciviato = potassioLisciviabile*(lisciviazione/100.)
    print potassioLisciviato

    doseK = fabbisognoColturale-potassioPrecedente+potassioLisciviato
    print doseK

    return doseK







