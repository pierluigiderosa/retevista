# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.gis import admin

from .models import stazioni_retevista,dati_orari,dati_aggregati_daily,dati_spi,iframe_stazioni
# Register your models here.

class dati_aggregatiAdmin(admin.ModelAdmin):
    list_display = ('stazione','data')
    list_filter = ('data',)
    date_hierarchy = 'data'

admin.site.register(stazioni_retevista, admin.OSMGeoAdmin)
admin.site.register(dati_orari)
admin.site.register(iframe_stazioni)
admin.site.register(dati_spi)
admin.site.register(dati_aggregati_daily,dati_aggregatiAdmin)
admin.site.site_header = "VISTA® Amministazione ReteVISTA"
admin.site.site_title = "VISTA"
admin.site.index_title = "VISTA® Amministrazione"