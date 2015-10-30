# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 18:32:21 2015

@author: Risto
eesmärk võtta ettevõtete aadressid ning leida neile geocodingu abil 
täpsed koordinaadid
"""
#######andmed sisse DataFrameina
import pandas as pd
import numpy as np
data=pd.read_csv("ariregister_2015_10_15.csv", sep=";", encoding="latin-1")
data.head(5)
#kirjeldav stat
data.describe()
#columnite nimed
list(data.columns.values)
#arvutame aadressi üheks variableks
data["kogu_aadress"]=data["asukoht_ettevotja_aadressis"]+" "+\
data["asukoha_ehak_tekstina"]+" Estonia"
#eemaldame read, kus aadressi pole
data=data.dropna(subset=['kogu_aadress'], how='all')
#indeksid õigeks
data=data.reindex(range(0,len(data)), method="ffill")
#teen tühjad veerud latitude ja longitude jaoks
data["lat"]=""
data["lon"]=""

##################################GEOCODING
from geopy import geocoders
#google APIga geocodings
geolocator = geocoders.GoogleV3()
#location=geolocator.geocode(data["kogu_aadress"][2])
#print((location.latitude, location.longitude))
#loobime prooviks läbi esimesed 2000 aadressi
for i in range(0,2000):
    try:
        location=geolocator.geocode(data["kogu_aadress"][i], timeout=10)
        data["lat"][i]=location.latitude
        data["lon"][i]=location.longitude
    #kui koordinaate ei saa, siis annab errori, prindib selle ja loobib järgmise i
    except AttributeError as error_message:
        print("Error: geocode failed on input %s with message %s"%\
        (data["kogu_aadress"][i], error_message))
        continue

#salvestame tulemused, et siis hiljem jätakata sama koha pealt
data.to_csv("29_10_2015_arireg.csv", sep=";")
   
#########################################GEOJSON
#Geojson formaati, et saaks visualiseerida
#subset andmetest
proov=data.head(1220)

# geojsoni formaadi näidis
template = \
    ''' \
    {  "geometry" : {
                "type" : "Point",
                "coordinates" : [%s,%s]},
        "properties" : { "name" : "%s"},
        "type" : "Feature"
        },
    '''
# geojsoni päis
output = \
    ''' \
{ "type" : "FeatureCollection",
    "features" : [
    '''
# loobime läbi andmefaili
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
  