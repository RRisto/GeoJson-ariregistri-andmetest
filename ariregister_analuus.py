# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 18:32:21 2015

@author: Risto
eesmärk võtta ettevõtete aadressid ning leida neile geocodingu abil 
täpsed koordinaadid
"""
#######andmed sisse DataFrameina
import pandas as pd
data=pd.read_csv("ariregister_2015_10_15.csv", sep=";", encoding="latin-1")
data.head(5)
#kirjeldav stat
data.describe()
#columnite nimed
list(data.columns.values)
#arvutame aadressi üheks variableks
data["kogu_aadress"]=data["asukoht_ettevotja_aadressis"]+" "+\
data["asukoha_ehak_tekstina"]+" Estonia"
#teen tühjad veerud latitude ja longitude jaoks
data["lat"]=""
data["lon"]=""

##################################GEOCODING
from geopy import geocoders
#google APIga geocodings
geolocator = geocoders.GoogleV3()
location=geolocator.geocode(data["kogu_aadress"][2])
print((location.latitude, location.longitude))
#loobime rahulikult koos viitajaga

for i in range(0,1000):
    location=geolocator.geocode(data["kogu_aadress"][i], timeout=10)
    data["lat"][i]=location.latitude
    data["lon"][i]=location.longitude
    
#########################################GEOJSON
#Geojson formaati, et saaks visualiseerida
#subset andmetest
proov=data.head(100)

# the template. where data from the csv will be formatted to geojson
template = \
    ''' \
    {  "geometry" : {
                "type" : "Point",
                "coordinates" : [%s,%s]},
        "properties" : { "name" : "%s"},
        "type" : "Feature"
        },
    '''
# the head of the geojson file
output = \
    ''' \
{ "type" : "FeatureCollection",
    "features" : [
    '''
# loop through the csv by row skipping the first
for i in range(0,len(proov)):
        lat = proov["lon"][i]
        lon = proov["lat"][i]
        name = proov["nimi"][i]
        output +=template % (proov["lon"][i], proov["lat"][i], proov["nimi"][i])       
# the tail of the geojson file
output += \
    ''' \
    ]
}
    '''

outFileHandle = open("output.geojson", "w")
outFileHandle.write(output)
outFileHandle.close()
####eemalda viimane koma failist käsitsi ja lae see üles geojson.io
  