# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin


from dash_aziende.models import Profile,campi,analisi_suolo,operazioni_colturali,\
    colture, macchinari,ColturaDettaglio,Trasporto,Magazzino,fasi_fenologiche

# Register your models here.

admin.site.register(campi, LeafletGeoAdmin)




class ProfileAdmin(admin.ModelAdmin):
    # exclude = ('cellulare',)
    pass

admin.site.register(Profile, ProfileAdmin)
admin.site.register(analisi_suolo)
admin.site.register(operazioni_colturali)

admin.site.register(colture)
admin.site.register(macchinari)
admin.site.register(ColturaDettaglio)
admin.site.register(Trasporto)
admin.site.register(Magazzino)
admin.site.register(fasi_fenologiche)
