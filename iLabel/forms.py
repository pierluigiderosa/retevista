from bootstrap_modal_forms.forms import BSModalForm
from django.contrib.gis import forms

from django.contrib.auth.models import User
from .models import prenotazione

class PrenotazioneForm(BSModalForm):
    class Meta:
        model = prenotazione
        fields = ['acquirente',
            'quantita',
            'coltura']
