from django.conf.urls import url
from .views import dati_orari_view,dati_giornalieri_view,dati_orari_list,points_view,mappa,export_dati_daily
from .models import stazioni_retevista

urlpatterns = [
    url(r'^orari/$', dati_orari_view, name='dati_orari'),
    url(r'^orari/(?P<uid>\d{1})$',dati_orari_view, name='dati_orari'),
    url(r'^export/(?P<uid>\d+)$',export_dati_daily, name='export_dati_daily'),
    url(r'^giornalieri/$',dati_giornalieri_view, name='dati_giornalieri'),
    url(r'^giornalieri/(?P<uid>\d{1})$',dati_giornalieri_view, name='dati_giornalieri'),
    url(r'^mappa/$',mappa,name='mappa-generale'),
    url(r'^api/geojson$', points_view.as_view(model=stazioni_retevista), name='data-stazioni'),
    url(r'^list/$', dati_orari_list),
    ]