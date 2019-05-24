from django.conf.urls import url
from .views import dati_orari_view,dati_giornalieri_view,dati_orari_list,points_view,mappa,export_dati_daily,MapAppezz,get_spi,ChartView,lista_stazioni_umbria_spi
from .models import stazioni_retevista
from consiglio.models import appezzamento

urlpatterns = [
    url(r'^orari/$', dati_orari_view, name='dati_orari'),
    url(r'^orari/(?P<uid>\d{1})$',dati_orari_view, name='dati_orari'),
    url(r'^export/(?P<uid>\d+)$',export_dati_daily, name='export_dati_daily'),
    url(r'^giornalieri/$',dati_giornalieri_view, name='dati_giornalieri'),
    url(r'^giornalieri/(?P<uid>\d{1})$',dati_giornalieri_view, name='dati_giornalieri'),
    url(r'^mappa/$',mappa,name='mappa-generale'),
    url(r'^api/geojson$', points_view.as_view(model=stazioni_retevista), name='data-stazioni'),
    url(r'^api/geojson.appezz$', MapAppezz.as_view(model=appezzamento), name='data-appezzamento'),
    url(r'^api/spi/(?P<uid>\d+)$', get_spi, name='api-data-spi'),
    url(r'^chart/(?P<uid>\d+)$', ChartView, name='chart-view-spi'),
    url(r'^list_spi/$',lista_stazioni_umbria_spi,name='lista-spi'),
    url(r'^list/$', dati_orari_list),
    ]