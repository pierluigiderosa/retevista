# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin
from .models import appezzamento,coltura,settore
# Register your models here.


class appezzamentoAdmin(admin.OSMGeoAdmin):
    list_display = ('nome','conduttore')
    #filter_horizontal = ('coltura',) solo many to many field

admin.site.register(appezzamento, appezzamentoAdmin)
admin.site.register(coltura)
admin.site.register(settore)