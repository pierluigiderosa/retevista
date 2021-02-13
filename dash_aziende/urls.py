from django.conf.urls import url

from .views import dashboard_fields, form_campi, add_profile, CampiGeoJson, form_analisi, dashboard_analisi, \
    CampoUpdateView, AnalisiUpdateView, form_coltura, \
    CampoDeleteView, ColtivazioneDeleteView, AnalisiDeleteView, dashboard_main, get_data_charts, \
    dash_operazioni_colturali, form_operazioni, \
    OperazioniDeleteView, edit_profile, dashboard_consiglio, dash_consumatore, main_biotipo, \
    CampiEstesiJson, dash_list_consumatore, operazioniJson, list_macchinari, iFoodPrint_detail, \
    form_macchinari, MacchinariDeleteView, MacchinariUpdateView, logistica_list, magazzini_list, \
    form_logistica_add, main_ifarm, main_iFoodPrint, AnalisiJson, form_magazzino_add, \
    iFoodPrint_panel, analisi_prodotti, analisi_prodotti_Add, macchinari_pdf, analisi_report_pdf, \
    autocomplete_fitofarmaci,autocomplete_malattie,autocomplete_erbe,print_quaderno,\
    elenco_quaderni,get_operazioni_data, get_bioclimatici
from .models import campi

urlpatterns = [
    url(r'^add/form/$',form_campi,name='form-campi'),
    url(r'^add/coltura/$',form_coltura,name='form-coltura'),
    url('update/form/(?P<pk>\d+)$', CampoUpdateView.as_view(), name='update-campi'),
    url('delete/coltivazione/(?P<pk>\d+)$', ColtivazioneDeleteView.as_view(), name='delete-coltivazione'),
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
    url('macchinari/pdf/$', macchinari_pdf, name='macchinari-pdf'),
    url(r'^macchinari/$',list_macchinari,name='lista-macchinari'),
    url(r'logistica/add$',form_logistica_add,name='add-logistica'),
    url(r'logistica/$',logistica_list,name='lista_logistica'),
    url(r'magazzini/$',magazzini_list,name='lista_magazzini'),
    url(r'magazzino/add/$',form_magazzino_add,name='add-magazzino'),
    url(r'^campi.geojson$', CampiGeoJson.as_view(model=campi), name='campi_geojson'),
    url(r'^campiEstesi.json$', CampiEstesiJson, name='campi_estesi_json'),
    url(r'^operazioni.json$', operazioniJson, name='operazioni_dettaglio_json'),
    url(r'analisi.json$',AnalisiJson,name='api-analisi-json'),
    url(r'^api/data/$', get_data_charts, name='api-data-dash'),
    url(r'^api/fitofarmaci/$', autocomplete_fitofarmaci, name='api-data-fitofarmaci'),
    url(r'^api/malattie/$', autocomplete_malattie, name='api-data-malattie'),
    url(r'^api/erbe/$', autocomplete_erbe, name='api-data-erbe'),
    url(r'^api/operazioni/$', get_operazioni_data, name='api-operazioni'),
    url(r'^api/bioclimatici/$', get_bioclimatici, name='api-bioclimatici'),
    url(r'^quadernicampagna/(?P<pk>\d+)/pdf/$', print_quaderno, name='quaderno-campagna'),
    url(r'^elenco_quaderni/$', elenco_quaderni, name='elenco-quaderni'),
    url(r'fields/$', dashboard_fields, name='main-fields'),
    url(r'analisi/(?P<pk>\d+)/pdf$',analisi_report_pdf,name='analisi-pdf'),
    url(r'analisi/$',dashboard_analisi,name='main-analisi'),
    url(r'analisi_prodotti/add/$',analisi_prodotti_Add,name='add-analisi-prodotto'),
    url(r'analisi_prodotti/$',analisi_prodotti,name='analisi-prodotti'),
    url(r'consiglio/$',dashboard_consiglio,name='main-consiglio'),
    url(r'forecast/$', dashboard_fields, {'forecast': True}, name='iland-forecast'),
    url(r'operazioni/$', dash_operazioni_colturali, name='main-operazioni-colturali'),
    url(r'consumatore/$', dash_list_consumatore, name='main-consumatore-list'),
    url(r'consumatore/(?P<uid>\d+)$', dash_consumatore, name='main-consumatore'),
    url(r'ifarm/$', main_ifarm, name='main-ifarm'),
    url(r'iFoodPrint/(?P<uid>\d+)$', iFoodPrint_detail, name='iFoodPrint-detail'),
    url(r'iFoodPrint_panel/(?P<uid>\d+)$', iFoodPrint_panel, name='iFoodPrint-panel'),
    url(r'iFoodPrint/$', main_iFoodPrint, name='main-iFoodPrint'),
    url(r'^biotipo/$',main_biotipo,name='main-biotopo'),
    url(r'^$', dashboard_main, name='main-iland')
]