import sys
import urllib, json
import rasterio
import numpy as np
from rasterio.features import shapes
from shapely.geometry import shape
import rasterio.mask
import os
from datetime import datetime

from django.contrib.gis.geos import GEOSGeometry
from dash_aziende.models import Landsat8Ndvi,campi

idcampo=13

url = "http://www.onegis.it/retevista/dashboard/campi.geojson?user=agricoltore&campo={}".format(idcampo)
idcampo=16
url='http://127.0.0.1:8000/dashboard/campi.geojson?user=agricoltore&campo={}'.format(idcampo)
response = urllib.urlopen(url)
data = json.loads(response.read())
print data


data['features'][0]['geometry']


geoms = [feature["geometry"] for feature in data['features']]


#reproject
from rasterio.warp import calculate_default_transform, reproject, Resampling

# dir_path = '/home/pierluigi/Sviluppo/retevista/landsat8'
dir_path = os.path.dirname(os.path.abspath(__file__))
for root, dirs, files in os.walk(dir_path):
    for filename in files:
        if filename.endswith('compressed.tiff'):
            data_string = filename[4:14]
            data_ndvi = datetime.strptime(data_string, '%Y-%m-%d')
            print(type(data_ndvi))
            print(data_ndvi)

            # ndvi_raster_path = '/home/pierluigi/Landsat8/ndvi2019-01-01-compressed.tiff'
            ndvi_raster_path = os.path.join(dir_path,filename)

            dst_crs = 'EPSG:4326' # CRS geographic
            # projected_ndvi_path = os.path.join(".","ndvi2019-01-01-reproject.tif")
            projected_ndvi_path = os.path.join(dir_path, 'ndvi' + data_string + '-reprojected.tiff', )

            with rasterio.open(ndvi_raster_path) as src:
                transform, width, height = calculate_default_transform(
                    src.crs, dst_crs, src.width, src.height, *src.bounds)
                kwargs = src.meta.copy()
                kwargs.update({
                    'crs': dst_crs,
                    'transform': transform,
                    'width': width,
                    'height': height
                })
                with rasterio.open(projected_ndvi_path, 'w', **kwargs) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=rasterio.transform,
                            src_crs=rasterio.crs,
                            dst_transform=transform,
                            dst_crs=dst_crs,
                            resampling=Resampling.nearest)
                dst.close()
            src.close()

            cropped_ndvi_path = os.path.join(dir_path, 'ndvi' + data_string + '-crop.tiff', )
            #crop ndvi map based on polygon
            with rasterio.open(projected_ndvi_path) as ndvi2:
                out_image, out_transform = rasterio.mask.mask(ndvi2, geoms,nodata=-2, crop=True)

                out_meta = ndvi2.meta
                out_meta.update({"driver": "GTiff",
                                 "height": out_image.shape[1],
                                 "width": out_image.shape[2],
                                 "transform": out_transform})
                with rasterio.open(cropped_ndvi_path, "w", **out_meta) as dest:
                    dest.write(out_image)
                dest.close()
            ndvi2.close()

            # raster polygonize
            cropped_ndvi_path = '/home/pierluigi/Sviluppo/retevista/landsat8/ndvi2019-01-01-crop.tiff'
            cropped_ndvi_path

            with rasterio.open(cropped_ndvi_path) as dataset:
                raster = dataset.read(1)
                crs = dataset.crs
                transform = dataset.transform
                epsg = crs['init'].lstrip('epsg:')
            dataset.close()

            mask = (raster > 0) & (raster < 0.1)
            shapes1 = shapes(np.float32(raster),mask=mask,transform=transform)

            results = (
                {'properties': {'raster_val': v}, 'geometry': s}
                for i, (s, v)
                in enumerate(
                shapes(np.float32(raster), mask=mask, transform=transform)))

            geom = list(results)
            print geom[0]

            for polygon, value in shapes(np.float32(raster), mask=mask, transform=transform):
                print shape(polygon)

                Landsat_Ndvi = Landsat8Ndvi(  # throws error here
                    geometry=GEOSGeometry(shape(polygon).wkt, srid=epsg),
                    giorno=data_ndvi,
                    rasterNdvi=cropped_ndvi_path,
                    campo=campi.objects.get(id=idcampo)
                )
                Landsat_Ndvi.save()

