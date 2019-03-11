# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin
from .models import appezzamento,coltura,settore
# Register your models here.


admin.site.register(appezzamento, admin.OSMGeoAdmin)
admin.site.register(coltura)
admin.site.register(settore)