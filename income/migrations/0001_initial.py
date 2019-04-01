# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-04-01 12:37
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='dati_aggregati_daily',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rain_cumulata', models.FloatField(blank=True, help_text='pioggia cumulata giornaliera', null=True, verbose_name='pioggia cum. giornaliera')),
                ('temp_min', models.FloatField(blank=True, null=True, verbose_name='Temp. min.')),
                ('temp_max', models.FloatField(blank=True, null=True, verbose_name='Temp. max')),
                ('temp_mean', models.FloatField(blank=True, null=True, verbose_name='Temp media')),
                ('humrel_min', models.FloatField(blank=True, null=True, verbose_name='Umid. rel. min')),
                ('humrel_max', models.FloatField(blank=True, null=True, verbose_name='Umid. rel. max')),
                ('solar_rad_mean', models.FloatField(blank=True, null=True, verbose_name='radiazione solare')),
                ('wind_speed_mean', models.FloatField(blank=True, null=True, verbose_name='Velocit\xe0 vento media')),
                ('note', models.CharField(default='', max_length=2500, verbose_name='Note')),
                ('data', models.DateField(verbose_name='Data & Ora')),
            ],
            options={
                'ordering': ('-data',),
            },
        ),
        migrations.CreateModel(
            name='dati_orari',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pioggia', models.FloatField(blank=True, help_text='pioggia cumulata giornaliera', null=True)),
                ('EvapoTras', models.FloatField(blank=True, null=True, verbose_name='Evapotraspirazione')),
                ('windSpeed', models.FloatField(blank=True, null=True, verbose_name='Velocit\xe0 del vento')),
                ('humRel', models.FloatField(blank=True, null=True, verbose_name='Umidit\xe0 relativa')),
                ('pressione', models.FloatField(blank=True, null=True, verbose_name='Pressione atm.')),
                ('solarRad', models.FloatField(blank=True, null=True, verbose_name='Radiazione solare')),
                ('dataora', models.DateTimeField(blank=True, null=True, verbose_name='Data & Ora')),
                ('rainrate', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Intesit\xe0 di pioggia ')),
                ('temp', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Temperatura \xb0C')),
                ('et_cum_year', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Et cum annuale')),
                ('et_cum_month', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Et cum mensile')),
                ('et_cum_day', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Et cum giornaliera')),
                ('rain_cum_year', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Rain cum annuale')),
                ('rain_cum_month', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Rain cum mensile')),
                ('rain_cum_day', models.FloatField(blank=True, default=0.0, null=True, verbose_name='Rain cum giornaliera')),
            ],
            options={
                'ordering': ('-dataora',),
            },
        ),
        migrations.CreateModel(
            name='stazioni_retevista',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.FloatField()),
                ('long', models.FloatField()),
                ('nome', models.CharField(max_length=20)),
                ('did', models.CharField(max_length=25)),
                ('geom', django.contrib.gis.db.models.fields.MultiPointField(srid=4326)),
            ],
            options={
                'verbose_name': 'stazione',
                'verbose_name_plural': 'stazioni',
            },
        ),
        migrations.AddField(
            model_name='dati_orari',
            name='stazione',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='income.stazioni_retevista'),
        ),
        migrations.AddField(
            model_name='dati_aggregati_daily',
            name='stazione',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='income.stazioni_retevista'),
        ),
    ]
