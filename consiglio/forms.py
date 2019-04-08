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
                  'Irr_mm',
            # 'Etc','P_ep',
                  # 'L',
                  # 'Lambda',
                  # 'a','Au',
                  # 'A','Irrigazione',
                  # 'stazione',
                  # 'appezzamento'
                  ]
