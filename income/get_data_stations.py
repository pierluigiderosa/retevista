import urllib, json
from datetime import datetime

url='http://api.weatherlink.com/v1/NoaaExt.json?user=001D0AF18D13&pass=retevista01'
response = urllib.urlopen(url)
data = json.loads(response.read())
print data
#data è un dizionario che contiene il dato


ora_oss = data['observation_time_rfc822']

datetime.strptime(ora_oss[5:-6], '%d %b %Y %H:%M:%S')


