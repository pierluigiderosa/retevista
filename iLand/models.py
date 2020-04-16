# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.db import models

class Shapefile(models.Model):
    tipologia_choices = [
        ('vincoli', 'vincoli'),
        ('catastale', 'catastale'),
    ]
    filename  = models.CharField(max_length=255)
    srs_epsg   = models.CharField(max_length=255)
    geom_type = models.CharField(max_length=50)
    tipologia = models.CharField(max_length=50,choices=tipologia_choices)

    def __str__(self):
        return '{} {}'.format(self.filename,self.id)


class Attribute(models.Model):
    shapefile = models.ForeignKey(Shapefile,
                                  on_delete=models.CASCADE)
    name      = models.CharField(max_length=255)
    type      = models.CharField(max_length=5)
    width     = models.IntegerField()
    precision = models.IntegerField()

    def __str__(self):
        return self.name


class Feature(models.Model):
    shapefile = models.ForeignKey(Shapefile,
                                  on_delete=models.CASCADE)
    # geom_point = models.PointField(srid=4326,
    #                                blank=True, null=True)
    # geom_multipoint = \
    #         models.MultiPointField(srid=4326,
    #                                blank=True, null=True)
    # geom_multilinestring = \
    #         models.MultiLineStringField(srid=4326,
    #                                     blank=True, null=True)
    geom_polygon = \
            models.PolygonField(srid=4326,
                                     blank=True, null=True)
    # geom_geometrycollection = \
    #         models.GeometryCollectionField(srid=4326,
    #                                        blank=True,
    #                                        null=True)

    objects = models.GeoManager()

    def __str__(self):
        return str(self.id)


class AttributeValue(models.Model):
    feature   = models.ForeignKey(Feature,
                                  on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute,
                                  on_delete=models.CASCADE)
    value     = models.CharField(max_length=255,
                                 blank=True, null=True)

    def __str__(self):
        return str(self.value)