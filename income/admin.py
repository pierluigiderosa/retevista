# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.gis import admin
from .models import stazioni_retevista,dati_orari,dati_aggregati_daily
# Register your models here.


admin.site.register(stazioni_retevista, admin.OSMGeoAdmin)
admin.site.register(dati_orari)
admin.site.register(dati_aggregati_daily)
