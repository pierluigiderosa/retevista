from PIL.ImageQt import rgb
from staticmap import StaticMap, Line, Polygon
from dash_aziende.models import campi
from django.core.files import File

def test():
    mapbox = 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4M29iazA2Z2gycXA4N2pmbDZmangifQ.-g_vE53SD2WrJ6tFX7QHmA '
    wikimedia = 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'
    argis = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{x}/{y}"
    pid=16
    podere = campi.objects.get(id=pid)
    # podere.geom.transform(3857)
    linea = Line(podere.geom.coords[0], 'red', 3)
    m = StaticMap(300, 400, 5, url_template=mapbox)
    # m.add_line(Line(((13.4, 52.5), (2.3, 48.9)), 'blue', 3))
    m.add_line(linea)
    image = m.render()
    image.save('map.png')


def podereMap(pid=16):
    wikimedia = 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'
    mapbox = 'http://tiles.mapbox.com/v4/openstreetmap.map-inh7ifmo/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoib3BlbnN0cmVldG1hcCIsImEiOiJncjlmd0t3In0.DmZsIeOW-3x-C5eX-wAqTw'
    argis = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{x}/{y}"
    google='https://mt1.google.com/vt/lyrs=s&x={x}%y={y}&z={z}'
    OSM = 'http://a.tile.osm.org/{z}/{x}/{y}.png'

    podere = campi.objects.get(id=pid)
    podere.geom.transform(3857)
    m = StaticMap(600, 340,10)
    # polygon = Polygon(podere.geom.coords[0], fill_color='rgb(255,255,255,1)', outline_color=None, simplify=False)
    linea = Line(podere.geom.coords[0], 'red', 3)
    # m.add_polygon(polygon)
    m.add_line(linea)
    image = m.render()
    image.save('map.png')
    reopen = open("map.png", "rb")
    django_file = File(reopen)
    podere.staticmap.save('map.png', django_file, save=True)
    reopen.close()


def all_podereMap():
    for podere in campi.objects.all():
        podereMap(podere.id)