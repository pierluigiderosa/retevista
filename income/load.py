import os
from django.contrib.gis.utils import LayerMapping
from .models import stazioni_retevista,stazioni_umbria

stazioni_retevista_mapping = {
    'lat' : 'lat',
    'long' : 'long',
    'nome' : 'nome',
    'did' : 'did',
    'geom' : 'MULTIPOINT',
}

stazioni_mapping = {
    'station_id' : 'station_id',
    'name' : 'name',
    'river_id' : 'river_id',
    'old_id_pt' : 'old_id_pt',
    'old_id_h' : 'old_id_h',
    'link' : 'link',
    'coord_n' : 'coord_n',
    'coord_e' : 'coord_e',
    'height' : 'height',
    'instrument' : 'instrument',
    'area' : 'area',
    'notes' : 'notes',
    'country' : 'country',
    'daily_prec' : 'daily_prec',
    'daily_temp' : 'daily_temp',
    'm_daily_fl' : 'm_daily_fl',
    'oid' : 'oid',
    'geom' : 'MULTIPOINT',
}


stazioni_retevista_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'stazioni_retevista.shp'),
)
stazioni_umbria_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'stazioni.shp'),
)

def run(verbose=True):
    lm = LayerMapping(
        stazioni_retevista, stazioni_retevista_shp, stazioni_retevista_mapping,
        transform=False, encoding='iso-8859-1',
    )
    lm.save(strict=True, verbose=verbose)


def run_umbria(verbose=True):
    lm = LayerMapping(
        stazioni_umbria, stazioni_umbria_shp, stazioni_mapping,
        transform=False, encoding='iso-8859-1',
    )
    lm.save(strict=True, verbose=verbose)