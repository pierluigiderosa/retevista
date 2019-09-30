# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bootstrap_modal_forms.generic import BSModalUpdateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView, CreateView
from djgeojson.views import GeoJSONLayerView

from django.contrib.gis.db.models import Extent, Union

from .models import campi,Profile,analisi_suolo
from dash_aziende.models import fertilizzazione as fert_model ,operazioni_colturali as oper_model,\
    irrigazione as irr_model, trattamento as tratt_model, semina as semina_model,raccolta as raccolta_model
from .forms import CampiAziendeForm,UserForm,ProfileForm,AnalisiForm,\
    FertilizzazioneForm,OperazioneColturaleForm,IrrigazioneForm,TrattamentoForm,SeminaForm,RaccoltaForm,\
    EditProfileForm
from forecast import get as get_forecast

# Create your views here.

@login_required
def dashboard_main(request):

    return render(request,"main_dash.html")

@login_required
def dashboard_fields(request,forecast=False):
    utente = request.user
    if utente.groups.filter(name='Agricoltori').exists():
        campi_all =  campi.objects.filter(proprietario=Profile.objects.filter(user=utente))
        staff = False
    if utente.is_staff or utente.groups.filter(name='Universita').exists():
        campi_all = campi.objects.all()
        staff=True
    latlong = []
    bbox = campi_all.aggregate(Extent('geom'))
    forecast_data = []
    for campo in campi_all:
        latlong.append([campo.geom.centroid.x,campo.geom.centroid.y])
        if forecast:
            forecast_single = get_forecast(campo.geom.centroid.y,campo.geom.centroid.x)
            forecast_data.append(forecast_single)
        else:
            forecast_data.append(None)
    areeKm2 = []
    campi3004 = campi_all.transform(3004, field_name='geom')
    for campo in campi3004:
        areeKm2.append(round(campo.geom.area/10000.,1)) #calcolo area in km2
    zipped = zip(campi_all, areeKm2,latlong,forecast_data)



    return render(request, "dashboard.html", {
        'campi':zipped,
        'staff': staff,
        'bbox': bbox['geom__extent'],
        'forecast': forecast
                                              })

@login_required
def dash_operazioni_colturali(request):
    # campi_all = campi.objects.filter(proprietario=Profile.objects.filter(user=request.user))
    # latlong = []
    # bbox = campi_all.aggregate(Extent('geom'))
    # tutte le tipologia di operazioni colturali
    tipologia_operazioni = oper_model.operazione_choices
    operazioni_all = oper_model.objects.filter(campo__proprietario=Profile.objects.filter(user=request.user))
    bbox = operazioni_all.aggregate(Extent('campo__geom'))
    return render(request,"operazioni_dashboard.html",{
        "tipologia_operazioni": tipologia_operazioni,
        "operazioni_all": operazioni_all,
        "bbox": bbox['campo__geom__extent'],

    })

@login_required
def dashboard_analisi(request):
    campi_all = campi.objects.filter(proprietario=Profile.objects.filter(user=request.user))
    analisi_all = analisi_suolo.objects.filter(campo__in=campi_all)
    bbox_condition = True
    if analisi_all.count() == 1:
        bbox_condition = False
    bbox = analisi_all.aggregate(Extent('geom'))


    return render(request,'analisi_dashboard.html',
                  {
                      'analisies':analisi_all,
                      'bbox': bbox['geom__extent'],
                      'bbox_condition': bbox_condition,
                  })

#inizio delle views per i forms ----
@login_required
def form_campi(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CampiAziendeForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            campo = form.save(commit=False)

            #automaticamente assegno il proprietario del campo
            if request.user.groups.filter(name='Agricoltori').exists():
                campo.proprietario = Profile.objects.get(user=request.user)

            campo.save()
            # process the data in form.cleaned_data as required
            # ...
            messages.success(request, 'Il tuo campo è stato aggiunto!')
            # redirect to a new URL:
            return redirect('main-fields')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CampiAziendeForm()
        if request.user.groups.filter(name='Agricoltori').exists():
            sel_proprietario =False
        if request.user.is_staff or request.user.groups.filter(name='Universita').exists():
            sel_proprietario =True

    return render(request, 'dashboard_form.html', {'form': form,'proprietario': sel_proprietario})


@login_required
def form_operazioni(request,oper_type=None):
    '''This function creates a brand new fertilizzazione object with related Book objects using inlineformset_factory'''
    query_campi_utente = campi.objects.filter(proprietario=Profile.objects.filter(user=request.user))
    #caso fertilizzazione
    if oper_type=='fertilizzazione':
        child_operation = fert_model()
        child_form = FertilizzazioneForm(instance=child_operation)  # setup a form for the parent


        OperationFormSet = inlineformset_factory(
            fert_model, oper_model,
            form=OperazioneColturaleForm,
            fields='__all__',
            fk_name='operazione_fertilizzazione',
            can_delete=False,
            extra=1,
        )

        if request.method == "POST":
            child_form = FertilizzazioneForm(request.POST,instance=child_operation)
            formset = OperationFormSet(request.POST, request.FILES,instance=child_operation)


            if child_form.is_valid():
                created_fertilizzazione = child_form.save(commit=False)
                formset = OperationFormSet(request.POST, request.FILES, instance=created_fertilizzazione)
                OperazioneColturaleForm.operazione=oper_type

                if formset.is_valid():
                    created_fertilizzazione.save()
                    operazioni = formset.save(commit=False)

                    for single_oper in operazioni:
                        single_oper.operazione=oper_type
                        single_oper.save()

                messages.success(request, 'la tua fertilizzazione è stata aggiunta!')
                # redirect to a new URL:
                return redirect('main-operazioni-colturali')

        else:
            child_form = FertilizzazioneForm(instance=child_operation)

            formset = OperationFormSet(instance=child_operation)
            for form in formset.forms:
                form.fields['campo'].queryset = query_campi_utente
    
    #caso irrigazione
    elif oper_type=='irrigazione':
        child_operation = irr_model()  #cambiare qui
        child_form = IrrigazioneForm(instance=child_operation)  # setup a form for the parent CAMBIARE QUI

        OperationFormSet = inlineformset_factory(
            irr_model, oper_model,   #CAMBIARE QUI
            form=OperazioneColturaleForm,
            fields='__all__',
            fk_name='operazione_irrigazione',  #CAMBIARE QUI
            can_delete=False, 
            extra=1,
        )

        if request.method == "POST":
            child_form = IrrigazioneForm(request.POST,instance=child_operation)  #CAMBIARE QUI
            formset = OperationFormSet(request.POST, request.FILES,instance=child_operation)

            if child_form.is_valid():
                created_fertilizzazione = child_form.save(commit=False)
                created_fertilizzazione.operazione = oper_type
                formset = OperationFormSet(request.POST, request.FILES, instance=created_fertilizzazione)

                if formset.is_valid():
                    created_fertilizzazione.save()
                    operazioni = formset.save(commit=False)

                    for single_oper in operazioni:
                        single_oper.operazione=oper_type
                        single_oper.save()

                messages.success(request, 'la tua irrigazione è stata aggiunta!')
                # redirect to a new URL:
                return redirect('main-operazioni-colturali')
        else:
            child_form = IrrigazioneForm(instance=child_operation) #CAMBIARE QUI
            formset = OperationFormSet(instance=child_operation)
            for form in formset.forms:
                form.fields['campo'].queryset = query_campi_utente

    #caso trattamento
    elif oper_type=='trattamento':
        child_operation = tratt_model()  #cambiare qui
        child_form = TrattamentoForm(instance=child_operation)  # setup a form for the parent CAMBIARE QUI

        OperationFormSet = inlineformset_factory(
            tratt_model, oper_model,   #CAMBIARE QUI
            form=OperazioneColturaleForm,
            fields='__all__',
            fk_name='operazione_trattamento',  #CAMBIARE QUI
            can_delete=False,
            extra=1,
        )

        if request.method == "POST":
            child_form = TrattamentoForm(request.POST,instance=child_operation)  #CAMBIARE QUI
            formset = OperationFormSet(request.POST, request.FILES,instance=child_operation)

            if child_form.is_valid():
                created_fertilizzazione = child_form.save(commit=False)
                created_fertilizzazione.operazione = oper_type
                formset = OperationFormSet(request.POST, request.FILES, instance=created_fertilizzazione)

                if formset.is_valid():
                    created_fertilizzazione.save()
                    operazioni = formset.save(commit=False)

                    for single_oper in operazioni:
                        single_oper.operazione=oper_type
                        single_oper.save()

                messages.success(request, 'il tuo trattamento è stato aggiunto!')
                # redirect to a new URL:
                return redirect('main-operazioni-colturali')
        else:
            child_form = TrattamentoForm(instance=child_operation) #CAMBIARE QUI
            formset = OperationFormSet(instance=child_operation)
            for form in formset.forms:
                form.fields['campo'].queryset = query_campi_utente

    #caso semina
    elif oper_type=='semina_trapianto':
        child_operation = semina_model()  #cambiare qui
        child_form = SeminaForm(instance=child_operation)  # setup a form for the parent CAMBIARE QUI

        OperationFormSet = inlineformset_factory(
            semina_model, oper_model,   #CAMBIARE QUI
            form=OperazioneColturaleForm,
            fields='__all__',
            fk_name='operazione_semina',  #CAMBIARE QUI
            can_delete=False,
            extra=1,
        )

        if request.method == "POST":
            child_form = SeminaForm(request.POST,instance=child_operation)  #CAMBIARE QUI
            formset = OperationFormSet(request.POST, request.FILES,instance=child_operation)

            if child_form.is_valid():
                created_fertilizzazione = child_form.save(commit=False)
                created_fertilizzazione.operazione = oper_type
                formset = OperationFormSet(request.POST, request.FILES, instance=created_fertilizzazione)

                if formset.is_valid():
                    created_fertilizzazione.save()
                    operazioni = formset.save(commit=False)

                    for single_oper in operazioni:
                        single_oper.operazione=oper_type
                        single_oper.save()

                messages.success(request, 'la tua semina è stata aggiunta!')
                # redirect to a new URL:
                return redirect('main-operazioni-colturali')
        else:
            child_form = SeminaForm(instance=child_operation) #CAMBIARE QUI
            formset = OperationFormSet(instance=child_operation)
            for form in formset.forms:
                form.fields['campo'].queryset = query_campi_utente

    #caso raccolta
    elif oper_type=='raccolta':
        child_operation = raccolta_model()  #cambiare qui
        child_form = RaccoltaForm(instance=child_operation)  # setup a form for the parent CAMBIARE QUI

        OperationFormSet = inlineformset_factory(
            raccolta_model, oper_model,   #CAMBIARE QUI
            form=OperazioneColturaleForm,
            fields='__all__',
            fk_name='operazione_raccolta',  #CAMBIARE QUI
            can_delete=False,
            extra=1,
        )

        if request.method == "POST":
            child_form = RaccoltaForm(request.POST,instance=child_operation)  #CAMBIARE QUI
            formset = OperationFormSet(request.POST, request.FILES,instance=child_operation)

            if child_form.is_valid():
                created_fertilizzazione = child_form.save(commit=False)
                created_fertilizzazione.operazione = oper_type
                formset = OperationFormSet(request.POST, request.FILES, instance=created_fertilizzazione)

                if formset.is_valid():
                    created_fertilizzazione.save()
                    operazioni = formset.save(commit=False)

                    for single_oper in operazioni:
                        single_oper.operazione=oper_type
                        single_oper.save()

                messages.success(request, 'la tua raccolta è stata aggiunta!')
                # redirect to a new URL:
                return redirect('main-operazioni-colturali')
        else:
            child_form = RaccoltaForm(instance=child_operation) #CAMBIARE QUI
            formset = OperationFormSet(instance=child_operation)
            for form in formset.forms:
                form.fields['campo'].queryset = query_campi_utente

    else:
        child_form=None
        formset=None
        oper_type=oper_type+' non ancora inserita. Contatta il gestore del sito'

    return render(request,"operazioni_form.html",{
        "child_form": child_form,
        "formset_operazione": formset,
        "titolo_child":oper_type,
    })



@login_required
def form_analisi(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AnalisiForm(request.user, request.POST)
        # check whether it's valid:
        if form.is_valid():
            analisi = form.save(commit=False)
            # process the data in form.cleaned_data as required
            # ...

            analisi.save()

            messages.success(request, 'la tua analisi è stata aggiunta!')
            # redirect to a new URL:
            return redirect('main-dashboard')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AnalisiForm(request.user)

    return render(request, 'analisi_form.html', {'form': form})


class CampoUpdateView(LoginRequiredMixin,UpdateView):
    model = campi
    template_name = 'dashboard_form.html'
    form_class = CampiAziendeForm
    success_message = 'Successo: Il campo è stato aggiornato.'
    success_url = reverse_lazy('main-fields')




class CampoDeleteView(LoginRequiredMixin,DeleteView):
    model = campi
    template_name = 'confirm_delete.html'
    success_message = 'Successo: Il campo è stato eliminato.'
    success_url = reverse_lazy('main-fields')

class AnalisiUpdateView(LoginRequiredMixin,UpdateView):
    model = analisi_suolo
    template_name = 'analisi_form.html'
    form_class = AnalisiForm
    success_message = "Successo: L'analisi è stata aggiornato."
    success_url = reverse_lazy('main-analisi')

    def get_form_kwargs(self):
        """This method is what injects forms with their keyword
            arguments."""
        # grab the current set of form #kwargs
        kwargs = super(AnalisiUpdateView, self).get_form_kwargs()
        # Update the kwargs with the user_id
        kwargs['user'] = self.request.user
        return kwargs


class AnalisiDeleteView(LoginRequiredMixin,DeleteView):
    model = analisi_suolo
    template_name = 'confirm_delete.html'
    success_message = '''Successo: L'analisi è stato eliminato.'''
    success_url = reverse_lazy('main-analisi')

class OperazioniDeleteView(LoginRequiredMixin,DeleteView):
    model = oper_model
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('main-operazioni-colturali')
    success_message = '''Successo: L'operazione è stata eliminata.'''


@login_required()
def get_data_charts(request):
    campi_all = campi.objects.filter(proprietario=Profile.objects.filter(user=request.user))
    campi_coltura_aggregati = campi_all.values('coltura__nome').annotate(Union('geom')).transform(3004)

    coltura = []
    area = []
    for campo_coltura in campi_coltura_aggregati:
        coltura.append(campo_coltura['coltura__nome'])
        area.append(round(campo_coltura['geom__union'].area/10000.,3))
    data = {
        "labels": coltura,
        "default": area,
    }
    return JsonResponse(data)




@login_required()
@transaction.atomic
def add_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            # process the data in form.cleaned_data as required
            user = user_form.save()

            user.refresh_from_db()  # This will load the Agricoltore Profile created by the Signal
            profile_form = ProfileForm(request.POST,
                                           instance=user.profile)  # Reload the profile form with the profile instance
            profile_form.full_clean()  # Manually clean the form this time. It is implicitly called by "is_valid()" method
            profile_form.save(commit=False)
            user_form.save()
            profile_form.save()  # Gracefully save the form
            grouppoAgricoltori = Group.objects.get(name='Agricoltori')
            user.groups.add(grouppoAgricoltori)
            messages.success(request, 'Il tuo profilo è stato creato!')
            # redirect to a new URL:
            return redirect('homepage')

        else:
            messages.error(request, 'Per favore correggi gli errori sotto.')
    else:
        user_form = UserForm()
        profile_form = ProfileForm()
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@login_required()
def edit_profile(request):
    editing_profile = False
    if Profile.objects.filter(user=request.user).exists():
        editing_profile = True

        if request.method == 'POST':
            form = EditProfileForm(request.POST, instance=request.user)
            profile_form = ProfileForm(request.POST, request.FILES,
                                       instance=request.user.profile)  # request.FILES is show the selected image or file

            if form.is_valid() and profile_form.is_valid():
                user_form = form.save()
                custom_form = profile_form.save(False)
                custom_form.user = user_form
                custom_form.save()
                messages.success(request, 'Il tuo profilo è stato aggiornato!')

                return redirect('homepage')
        else:
            form = EditProfileForm(instance=request.user)
            profile_form = ProfileForm(instance=request.user.profile)
            # args = {}
            # # args.update(csrf(request))
            # args['form'] = form
            # args['profile_form'] = profile_form
        return render(request, 'profile.html', {
            'user_form': form,
            'profile_form': profile_form,
            'edit_profile': editing_profile,
        })
    else:
        messages.warning(request,'Non si appartiene al gruppo degli agricoltori')
        return render(request,'profile.html',{
            'editing_profile': editing_profile,
        })





class CampiGeoJson(GeoJSONLayerView):
    # Options
    precision = 4  # float
    simplify = None  # generalization
    geom = 'geom'  # colonna geometrie
    properties = ['nome', ]

    def get_queryset(self):
        # pk_id = self.request.GET.get('agricoltore')
        context = campi.objects.filter(proprietario=Profile.objects.get(user=self.request.user))
        return context

class AnalisiGeoJson(GeoJSONLayerView):
    # Options
    precision = 4  # float
    simplify = 0.5  # generalization
    geom = 'geom'  # colonna geometrie
    properties = ['id_campione','data_segnalazione','campo','sabbia','limo','argilla','pH','OM','azoto','fosforo','potassio','scambio_cationico','den_apparente','pietrosita','profondita','note',]

    def get_queryset(self):
        # pk_id = self.request.GET.get('agricoltore')
        campi_all =  campi.objects.filter(proprietario=Profile.objects.get(user=self.request.user))
        context = analisi_suolo.objects.filter(campo__in=campi_all)
        return context