# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin


from .models import campi

# Register your models here.

admin.site.register(campi, LeafletGeoAdmin)