from django.conf.urls import url

from .views import dashboard_fields,form_campi,add_profile,CampiGeoJson,form_analisi,dashboard_analisi,\
    AnalisiGeoJson,CampoUpdateView,AnalisiUpdateView,\
    CampoDeleteView,AnalisiDeleteView,dashboard_main,get_data_charts,operazioni_colturali,form_operazioni
from .models import campi,analisi_suolo

urlpatterns = [
    url(r'^add/form/$',form_campi,name='form-campi'),
    url('update/form/(?P<pk>\d+)$', CampoUpdateView.as_view(), name='update-campi'),
    url('delete/form/(?P<pk>\d+)$', CampoDeleteView.as_view(), name='delete-campi'),
    url(r'^add/analisi/$',form_analisi,name='form-analisi'),
    url('update/analisi/(?P<pk>\d+)$', AnalisiUpdateView.as_view(), name='update-analisi'),
    url('delete/analisi/(?P<pk>\d+)$', AnalisiDeleteView.as_view(), name='delete-analisi'),
    url(r'^add/operazioni/$', form_operazioni, name='form-operazioni'),
    url(r'^registrazione/$',add_profile,name='add-profile'),
    url(r'^campi.geojson$', CampiGeoJson.as_view(model=campi), name='campi_geojson'),
    url(r'^analisi.geojson$', AnalisiGeoJson.as_view(model=analisi_suolo), name='analisi_geojson'),
    url(r'^api/data/$', get_data_charts, name='api-data-dash'),
    url(r'fields/$', dashboard_fields, name='main-fields'),
    url(r'analisi/$',dashboard_analisi,name='main-analisi'),
    url(r'forecast/$',dashboard_fields,{'forecast': True},name='main-forecast'),
    url(r'operazioni/$',operazioni_colturali,name='main-operazioni-colturali'),
    url(r'^$', dashboard_main, name='main-dashboard')
]