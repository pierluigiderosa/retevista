# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.gis import admin
from .models import stazioni_retevista,dati_orari,dati_aggregati_daily,quote_stazioni
# Register your models here.

class dati_aggregatiAdmin(admin.ModelAdmin):
    list_display = ('stazione','data')
    list_filter = ('data',)
    date_hierarchy = 'data'

admin.site.register(stazioni_retevista, admin.OSMGeoAdmin)
admin.site.register(dati_orari)
admin.site.register(quote_stazioni)
admin.site.register(dati_aggregati_daily,dati_aggregatiAdmin)
