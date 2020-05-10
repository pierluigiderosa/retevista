import requests
import json

def routing_test(startx=9.1512941,
                 starty=45.200458,
                 endx=12.4316389,
                 endy=43.0306353):
    my_token='5b3ce3597851110001cf6248d5ef9d00232549ce93723c97c790d81a'

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    }
    part1='https://api.openrouteservice.org/v2/directions/driving-car?api_key='


    path=part1+my_token+'&start='+str(startx)+','+str(starty)+'&end='+str(endx)+','+str(endy)
    # call = requests.get('https://api.openrouteservice.org/v2/directions/driving-car?api_key=5b3ce3597851110001cf6248d5ef9d00232549ce93723c97c790d81a&start=8.681495,49.41461&end=8.687872,49.420318', headers=headers)
    call = requests.get(path, headers=headers)
    print(call.status_code, call.reason)
    print(call.text)
    return call.text

def distanza(startx=9.1512941,
             starty=45.200458,
             endx=12.4316389,
             endy=43.0306353):

    x = routing_test(startx,starty,endx,endy)
    y = json.loads(x)
    distanza = y['features'][0]['properties']['segments'][0]['distance']
    return distanza

