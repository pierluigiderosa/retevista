# -*- coding: utf-8 -*-

import csv,os

from dash_aziende.models import colture as colture_model, \
    fasi_fenologiche, dataset_fitofarmaci, dataset_malattie, dataset_infestante

scelte_colture =[
'Actinidia',
'Aglio',
'Agretti',
'Albicocco',
'Altro',
'Amaranto',
'Arachide',
'Arancio',
'Artemisia',
'Asparago verde (turioni)',
'Avena',
'Avocado',
'Barbababietola da zucchero',
'Basilico',
'Bergamotto',
'Bietola',
'Broccoletto di rapa (cime di rapa)',
'Canapa',
'Carciofo',
'Cardo',
'Carota',
'Carrube',
'Cartamo',
'Castagno',
'Cavolo',
'Cavolo abissino',
'Cece',
'Cedro',
'Cetriolo',
'Cicerchia',
'Cicoria',
'Ciliegio acido',
'Ciliegio dolce',
'Cipolla',
'Clementine',
'Cocomero',
'Colza',
'Coriandolo',
'Cotogno',
'Endivie',
'Erba cipollina',
'Erba mazzolina',
'Erba medica',
'Erbai di graminacee',
'Erbai di graminacee e leguminose',
'Fagiolino',
'Fagiolo',
'Fagiolo dal occhio',
'Farro',
'Fava',
'Favino e Favetta',
'Festuca',
'Fico',
'Finocchio',
'Fragola',
'Girasole',
'Grano duro',
'Grano saraceno',
'Grano tenero',
'Kaki',
'Kenaf',
'Lampone',
'Lattuga',
'Lenticchia',
'Lime',
'Limone',
'Lino',
'Loglio',
'Loiessa',
'Loietto',
'Lupino',
'Luppolo',
'Mais',
'Mandarino',
'Mandorlo',
'Manioca',
'Melanzana',
'Melo',
'Melograno',
'Melone',
'Miglio',
'Mirtillo',
'Nespolo',
'Nocciolo',
'Noce',
'Olivo',
'Orzo',
'Panico',
'Patata',
'Peperone',
'Pero',
'Pesco',
'Pioppo',
'Pisello',
'Pistacchi',
'Pomodoro',
'Pompelmo',
'Porro',
'Prati',
'Prezzemolo',
'Quinoa',
'Rapa',
'Ravanello',
'Ravizzone',
'Ribes',
'Ricino',
'Riso',
'Rovo',
'Rucola',
'Scalogno',
'Sedano',
'Segale',
'Sesamo',
'Soia',
'Sorgo',
'Spelta',
'Spinacio',
'Sulla',
'Susino',
'Tabacco',
'Trifoglio',
'Triticale',
'Uva spina',
'Valerianella',
'Veccia',
'Vite',
'Zucca',
'Zucchino',
'Pascolo',
'Prati-pascoli',
'Te'
]





fasi_cereali= ['0 Germinazione',
               '1 sviluppo fogliare',
               '2 accestimento',
               '3 Levata',
               '4 Botticella',
               '5 emergenza infiorescenza, spigatura',
               '6 fioritura',
               '7 sviluppo della spiga',
               '8 Riempimento granella',
               '9 Senescenza']

fasi_olivo = ['SVILUPPO DELLE FOGLIE',
              'SVILUPPO DEI GERMOGLI',
              'SVILUPPO DEI BOTTONI FIORALI',
              'FIORITURA',
              'SVILUPPO DEI FRUTTI',
              'MATURAZIONE',
              'ENTRATA IN RIPOSO']


def popola_colture():
    for coltura in scelte_colture:
        singola_coltura_entry = colture_model(nome=coltura)
        singola_coltura_entry.save()

def popola_fasi_fenologiche():
    '''
    utilizzo:
    from dash_aziende.populate_data import popola_fasi_fenologiche
    popola_fasi_fenologiche()
    :return: Null - popola il db
    '''
    if colture_model.objects.filter(nome__exact='Grano duro').exists():
        cereale = colture_model.objects.get(nome__exact='Grano duro')
        for faseCereale in fasi_cereali:
            fase = fasi_fenologiche(fase=faseCereale,coltura_rif=cereale)
            fase.save()
    # if colture_model.objects.filter(nome__exact='Olivo').exists():
    #     olivo = colture_model.objects.get(nome__exact='Olivo')
    #     for faseCereale in fasi_olivo:
    #         fase = fasi_fenologiche(fase=faseCereale,coltura_rif=olivo)
    #         fase.save()


def popola_fitofarmaci():
    '''
    funziona per popolare i fitofarmaci
    :return: Null - popola il db
    '''

    with open('/home/pierluigi/Sviluppo/retevista/dash_aziende/data/Dataset_fitofarmaci.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                fitofarmaco = dataset_fitofarmaci(
                    NUMERO_REGISTRAZIONE=row[0],
                    FORMULATO=row[1],
                    PRODUTTORE=row[2],
                SOSTANZE_ATTIVE=row[3],
                SOSTANZA_ATTIVA_PER_100G_DI_PRODOTTO=row[4],
                                                  )
                fitofarmaco.save()
            line_count += 1
        print('saved %s fitofarmaci.' %line_count)


def popola_mattie():
    with open('/home/pierluigi/Sviluppo/retevista/dash_aziende/data/Malattie_parassiti.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                malattia = dataset_malattie(
                    gruppo=row[0],
                    malattia=row[1],
                )
                malattia.save()
            line_count += 1
        print('saved %s malattie.' %line_count)

def popola_infestanti():
    with open('/home/pierluigi/Sviluppo/retevista/dash_aziende/data/Infestanti.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                infestante = dataset_infestante(
                    gruppo=row[0],
                    infestante=row[1],
                )
                infestante.save()
            line_count += 1
        print('saved %s infestanti.' %line_count)