# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin
from .models import appezzamento,coltura,settore,bilancio,appezzamentoCampo
# Register your models here.


class appezzamentoAdmin(admin.OSMGeoAdmin):
    list_display = ('nome','conduttore')
    #filter_horizontal = ('coltura',) solo many to many field

class colturaAdmin(admin.OSMGeoAdmin):
    exclude = ('kc_ini','kc_med','kc_end','durata_kc_ini','durata_kc_dev','durata_kc_med','durata_kc_end',)

admin.site.register(appezzamento, appezzamentoAdmin)
admin.site.register(coltura,colturaAdmin)
admin.site.register(settore)
admin.site.register(bilancio)

admin.site.register(appezzamentoCampo)