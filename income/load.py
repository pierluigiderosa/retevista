import os
from django.contrib.gis.utils import LayerMapping
from .models import stazioni_retevista

stazioni_retevista_mapping = {
    'lat' : 'lat',
    'long' : 'long',
    'nome' : 'nome',
    'did' : 'did',
    'geom' : 'MULTIPOINT',
}


stazioni_retevista_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'stazioni_retevista.shp'),
)

def run(verbose=True):
    lm = LayerMapping(
        stazioni_retevista, stazioni_retevista_shp, stazioni_retevista_mapping,
        transform=False, encoding='iso-8859-1',
    )
    lm.save(strict=True, verbose=verbose)
