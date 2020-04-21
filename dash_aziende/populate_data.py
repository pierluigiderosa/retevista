# -*- coding: utf-8 -*-

from dash_aziende.models import colture as colture_model,\
    fasi_fenologiche

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





fasi_cereali= ['Germinazione',
               'sviluppo fogliare',
               'accestimento',
               'Levata',
               'Botticella',
               'emergenza infiorescenza, spigatura',
               'fioritura',
               'sviluppo della spiga',
               'Riempimento granella',
               'Senescenza']

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
    if colture_model.objects.filter(nome__exact='Frumento').exists():
        cereale = colture_model.objects.get(nome__exact='Frumento')
        for faseCereale in fasi_cereali:
            fase = fasi_fenologiche(fase=faseCereale,coltura_rif=cereale)
            fase.save()
    # if colture_model.objects.filter(nome__exact='Olivo').exists():
    #     olivo = colture_model.objects.get(nome__exact='Olivo')
    #     for faseCereale in fasi_olivo:
    #         fase = fasi_fenologiche(fase=faseCereale,coltura_rif=olivo)
    #         fase.save()


