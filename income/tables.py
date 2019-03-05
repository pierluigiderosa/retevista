# -*- coding: utf-8 -*-

import django_tables2 as tables

from .models import dati_orari,dati_aggregati_daily


class RainColumn(tables.Column):
    def render(self, value):
        return '{:0.2f} mm'.format(value)

class TempColumn(tables.Column):
    def render(self, value):
        return '{:0.1f} °C'.format(value)

class UmidColumn(tables.Column):
    def render(self, value):
        return '{:0.0f} %'.format(value)

class WindSpeedColumn(tables.Column):
    def render(self, value):
        return '{:0.1f} km/h'.format(value)

class SolarColumn(tables.Column):
    def render(self, value):
        return '{:0.0f} W/m2'.format(value)

class DatiOrariTable(tables.Table):
    temp = TempColumn()
    pioggia = RainColumn()
    EvapoTras = RainColumn()
    windSpeed = WindSpeedColumn()
    humRel = UmidColumn()
    solarRad = SolarColumn()


    class Meta:
        model = dati_orari
        exclude = [
            'id',
            "stazione"
                   ]
        sequence = ('dataora', '...')
        template_name = 'django_tables2/bootstrap4.html'


class DatiGiornalieriTable(tables.Table):
    rain_cumulata = RainColumn()
    temp_min = TempColumn()
    temp_max = TempColumn()
    temp_mean = TempColumn()
    humrel_min = UmidColumn()
    humrel_max = UmidColumn()
    solar_rad_mean = SolarColumn()
    wind_speed_mean = WindSpeedColumn()

    class Meta:
        model = dati_aggregati_daily
        exclude = [
            'id',
            #"stazione"
        ]
        template_name = 'django_tables2/bootstrap4.html'