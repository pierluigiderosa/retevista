import django_filters
from .models import dati_orari

class StazioniFilter(django_filters.FilterSet):
    release_year = django_filters.DateFilter(field_name='data', lookup_expr='day__gt')

    class Meta:
        model = dati_orari
        fields = {
            'stazione__nome':['icontains'],
                  }