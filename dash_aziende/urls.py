from django.conf.urls import url

from .views import dashboard,form_campi

urlpatterns = [
    url(r'^form/',form_campi,name='form-campi'),
    url(r'^$', dashboard,name='main-dashboard')
]