from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.gis import forms
from .models import bilancio,rasterAppezzamento
from bootstrap_modal_forms.forms import BSModalForm

class BilancioForm(BSModalForm):
    class Meta:
        model = bilancio
        fields = [
            'note',
                  # 'data_rif',
                  # 'pioggia_cum',
                  # 'Kc','Et0',
                  # 'dose',
                  #
                  #'Irr_mm',
            # 'Etc','P_ep',
                  # 'L',
                  # 'Lambda',
                  # 'a','Au',
                  # 'A','Irrigazione',
                  # 'stazione',
                  # 'appezzamento'
            'dose_antropica',
            'Irr_posticipata',
                  ]

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class RasterCasaForm(forms.ModelForm):
    class Meta:
        model = rasterAppezzamento
        fields = ('__all__')