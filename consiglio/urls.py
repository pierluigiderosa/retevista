from django.conf.urls import url

from .views import lista_appezzamenti,singolo_appezz

urlpatterns = [
    url(r'^appezz/(?P<uid>\d{1})$',singolo_appezz, name='singolo_appez'),
    url(r'^$', lista_appezzamenti,)
    ]