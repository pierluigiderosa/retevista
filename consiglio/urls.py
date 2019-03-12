from django.conf.urls import url

from .views import show_bilancio

urlpatterns = [
    url(r'^$', show_bilancio,)
    ]