# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render


from .forms import CampiAziendeForm

# Create your views here.


def dashboard(request):
    return render(request, "dashboard.html")

def form_campi(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CampiAziendeForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            form.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponse('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CampiAziendeForm()

    return render(request, 'dashboard_form.html', {'form': form})