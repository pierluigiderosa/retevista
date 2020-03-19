from django.conf.urls import url

from .views import dashboard_fields, form_campi, add_profile, CampiGeoJson, form_analisi, dashboard_analisi, \
    CampoUpdateView, AnalisiUpdateView, \
    CampoDeleteView, AnalisiDeleteView, dashboard_main, get_data_charts, dash_operazioni_colturali, form_operazioni, \
    OperazioniDeleteView, edit_profile, dashboard_consiglio, dash_consumatore, \
    CampiEstesiJson, dash_list_consumatore, operazioniJson, list_macchinari, \
    form_macchinari,MacchinariDeleteView,MacchinariUpdateView, logistica_list, form_logistica_add
from .models import campi

urlpatterns = [
    url(r'^add/form/$',form_campi,name='form-campi'),
    url('update/form/(?P<pk>\d+)$', CampoUpdateView.as_view(), name='update-campi'),
    url('delete/form/(?P<pk>\d+)$', CampoDeleteView.as_view(), name='delete-campi'),
    url(r'^add/analisi/$',form_analisi,name='form-analisi'),
    url('update/analisi/(?P<pk>\d+)$', AnalisiUpdateView.as_view(), name='update-analisi'),
    url('delete/analisi/(?P<pk>\d+)$', AnalisiDeleteView.as_view(), name='delete-analisi'),
    url(r'^add/operazioni/(?P<oper_type>\D+)/$', form_operazioni, name='form-operazioni'),
    url(r'^delete/operazione/(?P<pk>\d+)$', OperazioniDeleteView.as_view(), name='delete-operazioni'),
    url(r'^registrazione/$',add_profile,name='add-profilo-aziendale'),
    url(r'^update/registrazione/$', edit_profile, name='update-profilo-aziendale'),
    url(r'^macchinari/add/$',form_macchinari,name='form-macchinari'),
    url('macchinari/delete/(?P<pk>\d+)$', MacchinariDeleteView.as_view(), name='delete-macchinari'),
    url('macchinari/update/(?P<pk>\d+)$', MacchinariUpdateView.as_view(), name='update-macchinari'),
    url(r'^macchinari/$',list_macchinari,name='lista-macchinari'),
    url(r'logistica/add$',form_logistica_add,name='add-logistica'),
    url(r'logistica/$',logistica_list,name='lista_logistica'),
    url(r'^campi.geojson$', CampiGeoJson.as_view(model=campi), name='campi_geojson'),
    url(r'^campiEstesi.json$', CampiEstesiJson, name='campi_estesi_json'),
    url(r'^operazioni.json$', operazioniJson, name='operazioni_dettaglio_json'),
    url(r'^api/data/$', get_data_charts, name='api-data-dash'),
    url(r'fields/$', dashboard_fields, name='main-fields'),
    url(r'analisi/$',dashboard_analisi,name='main-analisi'),
    url(r'consiglio/$',dashboard_consiglio,name='main-consiglio'),
    url(r'forecast/$',dashboard_fields,{'forecast': True},name='main-forecast'),
    url(r'operazioni/$', dash_operazioni_colturali, name='main-operazioni-colturali'),
    url(r'consumatore/$', dash_list_consumatore, name='main-consumatore-list'),
    url(r'consumatore/(?P<uid>\d+)$', dash_consumatore, name='main-consumatore'),
    url(r'^$', dashboard_main, name='main-dashboard')
]