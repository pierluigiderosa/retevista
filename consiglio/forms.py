from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import bilancio
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
                  ]

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']