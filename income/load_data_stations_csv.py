import csv
import os
from datetime import datetime


def run(verbose=True):
    station_data_csv = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'data', 'Benedetti_Del_Rio.csv'),
    )


    #path =  "/home/pierluigi/Sviluppo/retevista/income/data/Benedetti_Del_Rio.csv" # Set path of new directory here

    from income.models import dati_orari # imports the model

    with open(station_data_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            dataora = datetime.strptime(row['Date & Time'], '%d/%m/%y %H:%M')

            p = dati_orari(
                pioggia=row['Rain - mm'],
                EvapoTras = row['ET - mm'],
                windSpeed = row['Wind Speed - km/h'],
                humRel = row['Hum - %'],
                pressione = row['Barometer - hPa'],
                solarRad = row['Solar Rad - W/m^2'],
                dataora = dataora,
                rainrate = row['Rain Rate - mm'],
                temp = row['Temp - C']
            )

            p.save()

    #list of income elements
    #['Rain - mm', 'ET - mm', 'Wind Speed - km/h', 'Wind Direction', 'Hum - %', 'Barometer - hPa', 'Solar Rad - W/m^2', 'Date & Time', 'Rain Rate - mm', 'Temp - C']

