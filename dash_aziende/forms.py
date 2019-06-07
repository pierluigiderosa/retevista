from django import forms

from django.views.generic import UpdateView
from leaflet.forms.widgets import LeafletWidget

from .models import campi

LEAFLET_WIDGET_ATTRS = {
    'map_height': '500px',
    'map_width': '100%',
    'display_raw': 'true',
    'map_srid': 4326,
}

class CampiAziendeForm(forms.ModelForm):

    class Meta:
        model = campi
        fields = ('nome','coltura', 'geom')
        widgets = {'geom': LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS)}



class EditCampiAziende(UpdateView):
    model = campi
    form_class = CampiAziendeForm
    template_name = 'dashboard_form.html'