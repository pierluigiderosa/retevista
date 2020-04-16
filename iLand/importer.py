import os, os.path, tempfile, zipfile
import shutil, traceback,json

import shapefile as pyshp
from pyproj import Proj, transform

from django.contrib.gis.geos.geometry import GEOSGeometry

from .models import Shapefile as shp_model,Feature,Attribute,AttributeValue

def import_data(shapefile,character_encoding,epsg,tipologia):
    # Extract the uploaded shapefile.

    fd,fname = tempfile.mkstemp(suffix=".zip")
    os.close(fd)

    f = open(fname, "wb")
    for chunk in shapefile.chunks():
        f.write(chunk)
    f.close()

    if not zipfile.is_zipfile(fname):
        os.remove(fname)
        return "Not a valid zip archive."

    zip = zipfile.ZipFile(fname)

    required_suffixes = [".shp", ".shx", ".dbf", ".prj"]
    has_suffix = {}
    for suffix in required_suffixes:
        has_suffix[suffix] = False

    for info in zip.infolist():
        suffix = os.path.splitext(info.filename)[1].lower()
        if suffix in required_suffixes:
            has_suffix[suffix] = True

    for suffix in required_suffixes:
        if not has_suffix[suffix]:
            zip.close()
            os.remove(fname)
            return "Archive missing required " + suffix + " file."

    shapefile_name = None
    dbf_name = None
    dst_dir = tempfile.mkdtemp()
    for info in zip.infolist():
        if info.filename.endswith(".shp"):
            shapefile_name = info.filename
        if info.filename.endswith(".dbf"):
            dbf_name = info.filename

        dst_file = os.path.join(dst_dir, info.filename)
        f = open(dst_file, "wb")
        f.write(zip.read(info.filename))
        f.close()
    zip.close()

    # Open the shapefile.
    1+1

    try:
        layer = pyshp.Reader(os.path.join(dst_dir, shapefile_name))
        shapefile_ok = True
    except:
        traceback.print_exc()
        shapefile_ok = False

    if not shapefile_ok:
        os.remove(fname)
        shutil.rmtree(dst_dir)
        return "Not a valid shapefile."

    if not layer.shapeType == 5:
        os.remove(fname)
        shutil.rmtree(dst_dir)
        return "Shapefile non poligonale"

    # Create our Shapefile object to represent the imported shapefile.

    shapefile_model = shp_model(filename=shapefile_name,
                                srs_epsg=epsg,
                                geom_type='Polygon',
                                tipologia=tipologia
                                )

    shapefile_model.save()

    # Store the shapefile's attribute definitions into the database.

    attributes = []
    layer_def = layer.fields
    for i in range(len(layer_def[1:])):
        field_def = layer_def[1:][i]
        attr = Attribute(shapefile=shapefile_model,
                        name=field_def[0],
                        type=field_def[1],
                        width=field_def[2],
                        precision=field_def[3])
        attr.save()
        attributes.append(attr)

    # Set up a coordinate transformation to convert from the shapefile's
    input_projection = Proj(init="epsg:{}".format(epsg))
    output_projection = Proj(init="epsg:4326")
    # Process each feature in turn.

    geom = layer.shapes()

    for featureID,feature in enumerate(geom):

        # if there is only one part
        if len(feature.parts) == 1:
            poly_list = []
            # get each coord that makes up the polygon

            #TODO: la  riproiezione
            # for coords in feature.points:
            #     x, y = coords[0], coords[1]
            #     # tranform the coord
            #     new_x, new_y = transform(input_projection, output_projection, x, y)

            #salvo i dati nel DB
            pp = feature.__geo_interface__
            geom_json = json.dumps(feature.__geo_interface__)
            feature_db = Feature(shapefile = shapefile_model,
                                 geom_polygon=geom_json,
                         )
            feature_db.save()

        # Store the feature's attribute values into the database.
        record = layer.record(featureID)
        for ij in range(len(attributes)):
            attr = attributes[ij]
            value = record[ij]
            attr_value = AttributeValue(feature=feature_db,
                                        attribute=attr,
                                        value=value)
            attr_value.save()

    os.remove(fname)
    shutil.rmtree(dst_dir)
    return None



