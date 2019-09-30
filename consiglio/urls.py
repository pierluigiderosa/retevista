from django.conf.urls import url

from .views import lista_appezzamenti,singolo_appezz,BilancioCreateView,BilancioUpdateView,export_appezz,get_data,ChartView,singolo_appezz_campo,ChartViewCampo,get_campi_data

urlpatterns = [
    url(r'^appezz/(?P<uid>\d+)$',singolo_appezz, name='singolo_appez'),
    url(r'^campo/(?P<uid>\d+)$',singolo_appezz_campo, name='singolo_appez_campo'),
    url(r'^export/(?P<uid>\d+)$',export_appezz, name='export_singolo_appez'),
    url(r'^create/$', BilancioCreateView.as_view(), name='create_bilancio'),
    url('update/(?P<pk>\d+)$', BilancioUpdateView.as_view(), name='update_bilancio'),
    url(r'^api/data/(?P<uid>\d+)$', get_data, name='api-data'),
    url(r'^api/campi/(?P<uid>\d+)$', get_campi_data, name='api-data-campi'),
    url(r'^chart/(?P<uid>\d+)$', ChartView, name='chart-view'),
    url(r'^chartcampo/(?P<uid>\d+)$', ChartViewCampo, name='chart-view-campo'),
    url(r'^$', lista_appezzamenti,name='lista-appezzamenti')
    ]