# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin


from .models import Profile,campi,analisi_suolo

# Register your models here.

admin.site.register(campi, LeafletGeoAdmin)




class ProfileAdmin(admin.ModelAdmin):
    # exclude = ('cellulare',)
    pass

admin.site.register(Profile, ProfileAdmin)
admin.site.register(analisi_suolo)