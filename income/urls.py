from django.conf.urls import url
from .views import dati_orari_view,dati_giornalieri_view,dati_orari_list

urlpatterns = [
    url(r'^orari/$', dati_orari_view, name='dati_orari'),
    url(r'^orari/(?P<uid>\d{1})$',dati_orari_view, name='dati_orari'),
    url(r'^giornalieri/$',dati_giornalieri_view, name='dati_giornalieri'),
    url(r'^giornalieri/(?P<uid>\d{1})$',dati_giornalieri_view, name='dati_giornalieri'),
    url(r'^list/$', dati_orari_list),
    ]