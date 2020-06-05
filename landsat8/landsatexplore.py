import tarfile
import rasterio
from rasterio import plot
import numpy as np
import os

import landsatxplore.api
api = landsatxplore.api.API('pierluigi.derosa', '10aprile')

download=False

scenesBboxL8= api.search(
     dataset='LANDSAT_8_C1',
     # bbox=(12.058475,42.7589474,13.203343,43.26102),
     latitude=43.1107,
     longitude=12.3908,
     start_date='2019-01-01',
     end_date='2020-03-03',
     max_cloud_cover=40)

print('{} scenes found.'.format(len(scenesBboxL8)))

for scene in scenesBboxL8:
     print(scene['acquisitionDate'])
     print(scene['entityId']) #id per il download
     print(scene['displayId']) #nome del file zip

api.logout()

scenesBboxL8=scenesBboxL8[:-1] ## TODO: da rimuovere dopo
#download delle scene
if download:
    from landsatxplore.earthexplorer import EarthExplorer
    ee = EarthExplorer('pierluigi.derosa','10aprile')
    for scene in scenesBboxL8:
         idDownload=scene['entityId']
         print('scarico '+scene['displayId'])
         ee.download(scene_id=scene['entityId'], output_dir='.')

    ee.logout()

#scompatto

## TODO: si deve ciclare su tutte le scene
for scena in scenesBboxL8:
    cartella = scena['displayId']
    dataAcquisizione = scena['acquisitionDate']
    # cartella ='LC08_L1TP_166051_20200206_20200211_01_T1'

    tar = tarfile.open(cartella+'.tar.gz', "r:gz")
    tar.extractall(path=cartella)
    tar.close()

    #calcolo del NDVI



    #band4 = rasterio.open('../Landsat8/LC08_L1TP_042035_20180603_20180615_01_T1_B4_clip.tif') #red
    band4=rasterio.open(cartella+'/'+cartella+'_B4.TIF') #red
    band5 = rasterio.open(cartella+'/'+cartella+'_B5.TIF') #nir
    #number of raster rows
    band4.height
    #number of raster columns
    band4.width
    #type of raster byte
    band4.dtypes[0]
    #raster sytem of reference
    band4.crs
    #raster transform parameters
    band4.transform
    #raster values as matrix array
    band4.read(1)

    #generate nir and red objects as arrays in float64 format
    red = band4.read(1).astype('float64')
    nir = band5.read(1).astype('float64')

    nir


    #ndvi calculation, empty cells or nodata cells are reported as 0
    ndvi=np.where(
        (nir+red)==0.,
        0,
        (nir-red)/(nir+red))
    ndvi[:5,:5]
    #export ndvi image
    ndviImage = rasterio.open('./ndvi'+dataAcquisizione+'.tiff','w',driver='Gtiff',
                              width=band4.width,
                              height = band4.height,
                              count=1, crs=band4.crs,
                              transform=band4.transform,
                              dtype='float64')
    ndviImage.write(ndvi,1)
    ndviImage.close()





#codice per usare diettamente l'applicazione
#/home/pierluigi/.local/bin/landsatxplore search --dataset LANDSAT_8_C1 --location 12.38 43.05 --start 2019-07-01 --end 2019-12-31 --clouds 10
