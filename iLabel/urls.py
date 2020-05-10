from django.conf.urls import url

from .views import iLabel_main, dash_list_consumatore, dash_consumatore, prenotazioneCreate

urlpatterns = [
    url(r'azienda/(?P<uid>\d+)$', dash_consumatore, name='main-azienda'),
    url(r'aziende/$', dash_list_consumatore, name='main-aziende-list'),
    url('prenotazione/add/', prenotazioneCreate.as_view(), name='crea-prenotazione'),
    url(r'^$', iLabel_main, name='main-ilabel')
]