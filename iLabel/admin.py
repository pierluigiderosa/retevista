# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis import admin

# Register your models here.
from iLabel.models import prenotazione

admin.site.register(prenotazione)
