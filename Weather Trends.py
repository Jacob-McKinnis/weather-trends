'''
Weather Trends 
Written by Jacob McKinnis

Script to compare historical weather data to the current forecast 

This requires the "requests" library. To install, run the command: "pip install requests"

To see the full list of allowed arguments, run "Weather Trends.py -h"

APIs:
Open Meteo
https://open-meteo.com/

Current forecast:
https://api.open-meteo.com/v1/forecast?

Historic Data:
https://archive-api.open-meteo.com/v1/archive?
'''

from datetime import datetime, timedelta
import csv
import json 
import argparse
import requests

CURRENT_DATE = datetime.today().strftime("%m-%d")
CURRENT_YEAR = int(datetime.today().strftime("%Y"))

parser = argparse.ArgumentParser("Weather Trends")
parser.add_argument("-lat","--latitude", type=float, required=True, help="<Required> The latitude of the location to check")
parser.add_argument("-lon","--longitude", type=float, required=True, help="<Required> The longitude of the location to check")
parser.add_argument("-p","--get_precip", type=bool, nargs='?', default=False, const=True, help="Switches from checking temperature to precipitation")
parser.add_argument("-d","--duration", type=int, nargs='?', default=1, help="The number of days to check. Allows integers in the range 1-5")
parser.add_argument("-y","--years", nargs='?', default=f"{CURRENT_YEAR-1}", type=str, help="A comma seperated list of years in the past to check. Ex. -y 2012,2010")
args = parser.parse_args()
DURATION = args.duration
if DURATION <1 or DURATION > 5:
    print("Invalid duration")
    quit()
ARCHIVE_YEARS = args.years.split(',')
GET_PRECIPITATION = args.get_precip

LATITUDE = args.latitude#40.4212
LONGITUDE = args.longitude#-79.7881

print(f"Getting the weather trends for {CURRENT_DATE} in {CURRENT_YEAR},{args.years}")

FORECAST_BASE_URL = "https://api.open-meteo.com/v1/forecast?"
ARCHIVE_BASE_URL = "https://archive-api.open-meteo.com/v1/archive?"

START_DATE = datetime.today()
END_DATE = START_DATE + timedelta(days=DURATION)

def pull_API_data(URL,lat,long,pull_year):
    start = START_DATE.replace(year=pull_year)
    end = END_DATE.replace(year=pull_year)
    params = {
        'latitude':lat,
        'longitude':long,
        'hourly':'temperature_2m',
        'temperature_unit':'fahrenheit',
        'start_date':start.strftime("%Y-%m-%d"),
        'end_date':end.strftime("%Y-%m-%d")
    }
    if GET_PRECIPITATION:
        params['precipitation_unit'] = 'inch'
        params['hourly'] = 'precipitation'
    
    headers = {
        'User-Agent': 'Weather Trends'
    }
    r = requests.get(url = URL, headers = headers, params= params)
    return json.loads(r.text)

def process_API_data(data):
    values = []
    weather_type = 'temperature_2m'
    if GET_PRECIPITATION:
        weather_type = 'precipitation'
        
    if data['hourly'] and data['hourly']['time'] and data['hourly'][weather_type]:
        for value in data['hourly'][weather_type]:
            values.append(value)
    return values

trends = {}
trends['hours'] = []
for hour in range(DURATION * 24):
    trends['hours'].append(hour)

# process current weather forecast
data = pull_API_data(FORECAST_BASE_URL, LATITUDE, LONGITUDE, CURRENT_YEAR)
trends[CURRENT_YEAR] = process_API_data(data)

# process past weather archive
for year in ARCHIVE_YEARS:
    archive_data = pull_API_data(ARCHIVE_BASE_URL, LATITUDE, LONGITUDE, int(year))
    trends[year] = process_API_data(archive_data)

with open(f"weather_trends_{'precipitation' if GET_PRECIPITATION else 'temperature'}_{CURRENT_DATE}.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerow(trends.keys())
    for i in range(len(trends['hours'])):
        row = []
        for column in trends.keys():
            row.append(trends[column][i])
        writer.writerow(row)