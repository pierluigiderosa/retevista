# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin

# Register your models here.

from models import Shapefile, Feature, \
Attribute, AttributeValue
admin.site.register(Shapefile, admin.ModelAdmin)
admin.site.register(Feature, admin.OSMGeoAdmin)
admin.site.register(Attribute, admin.ModelAdmin)
admin.site.register(AttributeValue, admin.ModelAdmin)