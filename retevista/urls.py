"""retevista URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings

from django.contrib.gis import admin
from income.views import home_page

urlpatterns = [
#    url(r'^admin/cron/', include('django_cron.admin_urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^dati/', include('income.urls')),
    url(r'^elaborazioni/', include('consiglio.urls')),
    url(r'dashboard/',include('dash_aziende.urls')),
    url(r'^iLabel/', include('iLabel.urls',namespace='iLabel')),
    url(r'^iLand/', include('iLand.urls',namespace='iLand')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^$', home_page, name='homepage')

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)