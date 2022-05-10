import ast
import requests
import numpy as np
import progressbar
import sqlite3
import time
import os

#Pavage
Resolution=10
xFrance=np.linspace(48.113736,48.260228,Resolution)
yFrance=np.linspace(2.533400,4.301212,Resolution)


conn = sqlite3.connect('vent.db')
cursor=conn.cursor()


bar = progressbar.ProgressBar(max_value=Resolution**2)

listVent=[]


t=int(time.time())
cursor.execute('CREATE TABLE vent(vitesse NUMERIC, angle INT, latitude NUMERIC, longitude NUMERIC,INT temps)')
for i in range(Resolution):
    listVent+=[[]]
    for j in range(Resolution):
        responseWeathAPI = requests.get("https://api.openweathermap.org/data/2.5/weather?lat="+str(xFrance[i])+"&lon="+str(yFrance[j])+"&appid=8d783ab74b4115119149be5668440f2c")
        Weather = ast.literal_eval((responseWeathAPI.content).decode("UTF-8"))
        ventij=Weather["wind"]
        listVent[i]+=[ventij["speed"]]
        print("Coordonnées : x="+str(xFrance[i])+", y="+str(yFrance[j])+" vent : "+str(ventij["speed"])+"m/s\n")
        cursor.execute("INSERT INTO vent VALUES ("+str(ventij["speed"])+","+str(ventij["deg"])+","+str(xFrance[i])+","+str(yFrance[j])+","+str(t)+")")
        bar.update(Resolution*i+j)


conn.commit()
conn.close()