# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.gis import forms
from django.forms import SelectDateWidget
from django.forms.models import inlineformset_factory
from django.views.generic import UpdateView
from leaflet.forms.widgets import LeafletWidget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit,HTML

from .models import Profile, campi, analisi_suolo, \
    fertilizzazione, irrigazione, semina, trattamento, raccolta, \
    operazioni_colturali, macchinari, Trasporto, \
    ColturaDettaglio, raccolta_paglia, diserbo

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
        fields = ('nome', 'geom','proprietario')
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
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name'
        )

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
            'geom': LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS),
            'sabbia': forms.NumberInput(attrs={'v-model':"sabbia"}),
            'argilla': forms.NumberInput(attrs={'v-model': "argilla"}),
            'limo': forms.NumberInput(attrs={'v-model': "limo"})
        }

    def __init__(self, user, *args, **kwargs):
        super(AnalisiForm, self).__init__(*args, **kwargs)
        # if self.instance.pk is None:
        if user.is_staff or user.groups.filter(name='Universita').exists():
            self.fields['campo'].queryset = campi.objects.all()
        else:
            self.fields['campo'].queryset = campi.objects.filter(proprietario=Profile.objects.filter(user=user))
        # else:  # it's an UpdateView:
        # personalizzare il layout del form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('data_segnalazione', css_class='form-group col-md-3 mb-0'),
                Column('campo', css_class='form-group col-md-3 mb-0'),
                Column('id_campione',css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('sabbia', css_class='form-group col-md-3 mb-0'),
                Column('limo', css_class='form-group col-md-3 mb-0'),
                Column('argilla', css_class='form-group col-md-3 mb-0'),
                # HTML('''<p>somme delle percentuali [[ somma ]]%</p>'''),
                HTML('''<p>tessitura: [[ tessituraF ]]</p>'''),
                css_class='form-row',
                css_id='form-analisi'

            ),
            Row(
                Column('pH', css_class='form-group col-md-2 mb-0'),
                Column('OM', css_class='form-group col-md-2 mb-0'),
                Column('azoto', css_class='form-group col-md-2 mb-0'),
                Column('fosforo', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('CACO3_tot',css_class='form-group col-md-3 mb-0'),
                Column('CACO3_att',css_class='form-group col-md-3 mb-0'),
                Column('conduttivita_elettrica',css_class='form-group col-md-3 mb-0')
            ),
            Row(
                Column('potassio', css_class='form-group col-md-2 mb-0'),
                Column('scambio_cationico', css_class='form-group col-md-2 mb-0'),
                Column('den_apparente', css_class='form-group col-md-2 mb-0'),
                Column('pietrosita', css_class='form-group col-md-2 mb-0'),
                Column('profondita', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Row(
              Column('cap_di_campo', css_class='form-group col-md-4 mb-0'),
              Column('punto_appassimento', css_class='form-group col-md-4 mb-0'),
            ),
            'note',
            # 'geom',
            Submit('submit', 'Invia')
        )

    def clean(self):
        sabbia = self.cleaned_data['sabbia']
        limo = self.cleaned_data['limo']
        argilla = self.cleaned_data['argilla']
        argilla=float(argilla)
        limo = float(limo)
        sabbia = float(sabbia)
        totale = argilla+limo+sabbia
        if totale <99 or  totale > 101:
            self.add_error("sabbia",'la somma non fa 100%')
            self.add_error("limo", 'la somma non fa 100%')
            self.add_error("argilla", 'la somma non fa 100%')

        return self.cleaned_data

class ColturaDettaglioForm(forms.ModelForm):
    class Meta:
        model =ColturaDettaglio
        fields = '__all__'

        widgets = {'data_semina': DateInput(),
                   'data_raccolta': DateInput(),
                   'data_inizio': DateInput()}



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

class IrrigazioneForm(forms.ModelForm):
    class Meta:
        model = irrigazione
        fields = '__all__'

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False # This is crucial.

        helper.layout = Layout(
            Fieldset('Aggiungi una nuova irrigazione', 'irrigazione'),
        )

        return helper


class SeminaForm(forms.ModelForm):
    class Meta:
        model = semina
        fields = '__all__'

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False # This is crucial.

        helper.layout = Layout(
            Fieldset('Aggiungi una nuova semina', 'semina'),
        )

        return helper


class TrattamentoForm(forms.ModelForm):
    class Meta:
        model = trattamento
        fields = '__all__'

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False # This is crucial.

        helper.layout = Layout(
            Fieldset('Aggiungi un nuovo trattamento', 'trattamento'),
        )

        return helper

class RaccoltaForm(forms.ModelForm):
    class Meta:
        model = raccolta
        fields = '__all__'

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False # This is crucial.

        helper.layout = Layout(
            Fieldset('Aggiungi una nuova raccolta', 'raccolta'),
        )

        return helper

class RaccoltaPagliaForm(forms.ModelForm):
    class Meta:
        model = raccolta_paglia
        fields = '__all__'

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False # This is crucial.

        helper.layout = Layout(
            Fieldset('Aggiungi una nuova raccolta di paglia', 'raccolta'),
        )

        return helper

class DiserboForm(forms.ModelForm):
    class Meta:
        model = diserbo
        fields = '__all__'

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False # This is crucial.

        helper.layout = Layout(
            Fieldset('Aggiungi un nuovo diserbo', 'diserbo'),
        )

        return helper

class OperazioneColturaleForm(forms.ModelForm):
    class Meta:
        model=operazioni_colturali
        # fields='__all__'
        exclude = ('note','campo','operazione',
                   'operazione_fertilizzazione','operazione_irrigazione',
                   'operazione_raccolta',
                   'operazione_trattamento','operazione_semina',
                   'operazione_aratura','operazione_raccolta_paglia',
                   'operazione_diserbo')
        widgets={
            'data_operazione': DateInput(),
        }

class MacchinariForm(forms.ModelForm):

    class Meta:
        model = macchinari
        fields =  ('tipo_macchina','nome','descrizione',
                   'marca','modelloMacchinario','potenza',
                   'anno','targa','telaio','data_acquisto',
                   'data_revisione','data_controllo','libretto_circolazione',
                   'documento_assicurazione','manuale_uso','altri_allegati','azienda',
                   )
        widgets = {'data_acquisto': DateInput(),
                   'data_controllo': DateInput(),
                   'data_revisione': DateInput()}




class TrasportiForm(forms.ModelForm):
    class Meta:
        model = Trasporto
        fields = '__all__'
        widgets = {'data': DateInput(), }
