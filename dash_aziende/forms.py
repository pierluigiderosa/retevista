# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.gis import forms
from django.forms import SelectDateWidget
from django.forms.models import inlineformset_factory
from django.views.generic import UpdateView
from leaflet.forms.widgets import LeafletWidget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset

from .models import Profile, campi, analisi_suolo,\
    fertilizzazione,operazioni_colturali

LEAFLET_WIDGET_ATTRS = {
    'map_height': '500px',
    'map_width': '100%',
    # 'display_raw': 'false',
    'map_srid': 4326,
}

class CustomLeafletWidget(LeafletWidget):
    geometry_field_class = 'YourGeometryField'

class CampiAziendeForm(forms.ModelForm):

    class Meta:
        model = campi
        fields = ('nome','coltura', 'geom')
        widgets = {'geom': LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS)}


class EditCampiAziende(UpdateView):
    model = campi
    form_class = CampiAziendeForm
    template_name = 'dashboard_form.html'


class CampiAziendeFormBase(forms.ModelForm):
    class Meta:
        model = campi
        fields = ('nome','coltura', 'geom')
        widget= forms.BaseGeometryWidget(
            attrs={'map_width': 200,
                   'map_height': 200,
                   'template_name': 'gis/openlayers-osm.html',
                   'default_lat': 43,
                   'default_lon': 12,
                   'map_srid' : 4326,
                   }
        )

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password','first_name', 'last_name', 'email')
        widgets = {
            # telling Django your password field in the mode is a password input on the template
            'password': forms.PasswordInput
        }

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)
        fields = '__all__'

class DateInput(forms.DateInput):
    input_type = 'date'

class YourMapWidget(LeafletWidget):
    geometry_field_class = 'YourGeometryField'

class AnalisiForm(forms.ModelForm):
    class Meta:
        model = analisi_suolo
        fields = '__all__'
        widgets = {
            'data_segnalazione': DateInput(),
            'geom': LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS)
        }

    def __init__(self, user, *args, **kwargs):
        super(AnalisiForm, self).__init__(*args, **kwargs)
        # if self.instance.pk is None:
        self.fields['campo'].queryset = campi.objects.filter(proprietario=Profile.objects.filter(user=user))
        # else:  # it's an UpdateView:
        #     self.fields['campo'].queryset = campi.objects.filter(proprietario=Profile.objects.filter(user=self.instance.user))  # active users + self.instance.user

class FertilizzazioneForm(forms.ModelForm):
    class Meta:
        model = fertilizzazione
        fields = '__all__'


    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False # This is crucial.

        helper.layout = Layout(
            Fieldset('Aggiungi un nuovo fertilizzante', 'fertilizzante'),
        )

        return helper


class OperazioneColturaleForm(forms.ModelForm):
    class Meta:
        model=operazioni_colturali
        fields='__all__'
        widgets={
            'data_operazione': DateInput(),
        }