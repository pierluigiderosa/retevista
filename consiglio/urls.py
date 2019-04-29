from django.conf.urls import url

from .views import lista_appezzamenti,singolo_appezz,BilancioCreateView,BilancioUpdateView,export_appezz

urlpatterns = [
    url(r'^appezz/(?P<uid>\d+)$',singolo_appezz, name='singolo_appez'),
    url(r'^export/(?P<uid>\d+)$',export_appezz, name='export_singolo_appez'),
    url(r'^create/$', BilancioCreateView.as_view(), name='create_bilancio'),
    url('update/(?P<pk>\d+)$', BilancioUpdateView.as_view(), name='update_bilancio'),
    url(r'^$', lista_appezzamenti,name='lista-appezzamenti')
    ]