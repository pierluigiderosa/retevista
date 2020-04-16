from django.conf.urls import url

from .models import Feature
from .views import homepage_iLand,main_biotipo,catastino,\
    list_shapefiles,import_shapefile,report_vincoli,ricerca,vincoli_pdf

urlpatterns = [
    url(r'^biotipo/$',main_biotipo,name='main-biotopo'),
    url(r'^ricerca/$',ricerca,name='ricerca-catastale'),
    url(r'^report_vincoli/$',report_vincoli,name='report-vincoli'),
    url(r'^report_vincoli_pdf/$', vincoli_pdf, name='pdf-vincoli'),
    url(r'^catastino/$',catastino,name='catastino'),
    url(r'^import$', import_shapefile,name='import_shapes'),
    url(r'^lista_shapefiles/$', list_shapefiles,name='list_shapes'),
    url(r'^$', homepage_iLand, name='main-iland'),
]