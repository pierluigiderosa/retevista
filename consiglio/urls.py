from django.conf.urls import url

from .views import lista_appezzamenti,singolo_appezz,BilancioCreateView,BilancioUpdateView

urlpatterns = [
    url(r'^appezz/(?P<uid>\d{1})$',singolo_appezz, name='singolo_appez'),
    url(r'^create/$', BilancioCreateView.as_view(), name='create_bilancio'),
    url('update/(?P<pk>\d{1})$', BilancioUpdateView.as_view(), name='update_bilancio'),
    url(r'^$', lista_appezzamenti,name='lista-appezzamenti')
    ]