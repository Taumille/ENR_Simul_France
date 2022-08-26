import sqlite3
import pyproj
import progressbar
import requests
import ast
import urllib.parse
import json
import math
import matplotlib.pyplot as plt
import numpy as np

def Regroup():
    def formateTexte(nc):
        nc=str(nc)
        sortie=""
        for lettre in (nc):
            if lettre=='"' or lettre=="'":
                sortie+=" "
            else:
                sortie+=lettre
        return sortie

    pdefault=2

    print("Connexion à la base de données")
    conn=sqlite3.connect("eolienne.db")
    c=conn.cursor()
    print("Connecté")

    print("Récupération des valeurs utilisées")
    c.execute("SELECT * FROM used")
    used=c.fetchall()
    for k in range(len(used)):
        used[k]=used[k][0]

    c.execute("SELECT * FROM eolFiltre")

    liste=c.fetchall()
    print("Valeurs récupérées")

    try:
        c.execute('DROP TABLE eolFiltreGroup')
    except:
        pass
    c.execute('CREATE TABLE eolFiltreGroup (nomCommun	TEXT,PuissanceNominale	NUMERIC,ids	TEXT, idInit INT)')

    listNomCommun=[]
    print("Écriture en cours")

    bar=progressbar.ProgressBar(max_value=len(liste))

    for i in range(len(liste)):
        bar.update(i)
        if liste[i][1] != 'Null' and i != len(liste) - 1 and not (liste[i][0] in used):
            nomCommun = formateTexte(liste[i][1])
            ptot = 0
            ids = "["
            for j in range(i, len(liste)):
                if formateTexte(liste[j][1]) == nomCommun:
                    if liste[j][24] != 'Null':
                        ptot += float(liste[j][24])
                        pdefault = float(liste[j][24])
                    elif liste[j][41] != 'Null':
                        ptot += float(liste[j][41])
                        pdefault = float(liste[j][41])
                    else:
                        ptot += pdefault

                    used += [liste[j][0]]
                    c.execute("INSERT INTO used VALUES(" + str(liste[j][0]) + ")")

                    ids += str(liste[j][0]) + ","
            ids = ids[:-1]
            ids += "]"

            c.execute('INSERT INTO eolFiltreGroup VALUES("' + nomCommun + '",' + str(ptot) + ",'" + ids + "',"+str(liste[i][0])+")")

        if liste[i][4]!='Null' and i!=len(liste)-1 and not(liste[i][0] in used):
            nomCommun=formateTexte(liste[i][4])
            ptot=0
            ids="["
            for j in range(i,len(liste)):
                if formateTexte(liste[j][4])==nomCommun:
                    if liste[j][24] != 'Null':
                        ptot += float(liste[j][24])
                        pdefault = float(liste[j][24])
                    elif liste[j][41] != 'Null':
                        ptot += float(liste[j][41])
                        pdefault = float(liste[j][41])
                    else:
                        ptot+=pdefault

                    used+=[liste[j][0]]
                    c.execute("INSERT INTO used VALUES(" + str(liste[j][0]) + ")")

                    ids+=str(liste[j][0])+","

            ids=ids[:-1]
            ids+="]"

            c.execute('INSERT INTO eolFiltreGroup VALUES("' + nomCommun + '",' + str(ptot) + ",'" + ids + "',"+str(liste[i][0])+")")

    conn.commit()
    conn.close()

def Verif():
    conn=sqlite3.connect("eolienne.db")
    c=conn.cursor()

    c.execute("SELECT* FROM eolfiltre")
    liste=c.fetchall()

    c.execute("SELECT * FROM used")
    used=c.fetchall()
    conn.close()
    compteurNull = 0
    compteur=0
    for k in range(len(used)):
        used[k]=used[k][0]

    for k in range(len(liste)):
        if not(k in used):
            compteur+=1
            if [liste[k][24],liste[k][41]]==['Null','Null']:
                compteurNull+=1
    print(compteur)
    print(compteurNull)

def coord():
    def degtodec(s):
        lecteur = 0
        deg = ""
        min = ""
        sec = ""
        while s[lecteur] != "°" and s[lecteur] != "/":
            deg += s[lecteur]
            lecteur += 1
        lecteur += 1
        while s[lecteur] != "'" and s[lecteur] != "’" and s[lecteur] != "/":
            min += s[lecteur]
            lecteur += 1
        lecteur += 1
        while s[lecteur] != "'" and s[lecteur] != "’" and len(s) != lecteur + 1:
            sec += s[lecteur]
            lecteur += 1
        if sec[0]==".":
            sec="0"+sec
        return float(deg) + float(min) / 60 + float(sec) / 3600

    def retire_tiret(s):
        s_f=""
        for i in range(len(s)):
            if s[i]=="_":
                s_f+=" "
            else:
                s_f+=s[i]
        return s_f

    print("Connexion à la base...;;")
    conn=sqlite3.connect("eolienne.db")
    c=conn.cursor()
    print("Base connectée !")

    x_pcIndex=7
    y_pcIndex=8
    EPSG_Index=45
    X_Index=46
    Y_Index=47
    XLamb93_Index=60
    YLamb93_Index=61
    XIcpe_Index=70
    YIcpe_Index=71
    XCoord_ICPE=77
    YCoord_ICPE=78
    nc=[]


    print("Récupération des données...")
    c.execute("SELECT * FROM eolFiltre")
    liste=c.fetchall()
    print("Données récupérées !\nCréation de la table de données...")
    c.execute("DROP TABLE eolCoord")
    c.execute("CREATE TABLE eolCoord (gid INTEGER,lat NUMERIC,long NUMERIC)")
    print("Table des données reinitialisée !")
    print("Conversion en cours...")

    puissance_non_traite=0

    bar=progressbar.ProgressBar(max_value=len(liste))
    for k in range(len(liste)):
        bar.update(k)
        if liste[k][x_pcIndex]!='Null' and liste[k][y_pcIndex]!='Null' and not("°" in str(liste[k][x_pcIndex])):
            (x,y)=(liste[k][x_pcIndex],liste[k][y_pcIndex])

            proj = pyproj.Transformer.from_crs(2154, 4326, always_xy=True)
            (long,lat)=proj.transform(x,y)
            if lat<40:
                proj = pyproj.Transformer.from_crs(27572, 4326, always_xy=True)
                (long, lat) = proj.transform(x, y)
                if lat<40:
                    (long,lat)=(x,y)
            c.execute("INSERT INTO eolCoord VALUES("+str(liste[k][0])+","+str(lat)+","+str(long)+")")

        elif liste[k][x_pcIndex]!='Null' and liste[k][y_pcIndex]!='Null' and "°" in str(liste[k][x_pcIndex]):
            (x,y)=(liste[k][x_pcIndex],liste[k][y_pcIndex])

            (long, lat)=(degtodec(x),degtodec(y))
            c.execute("INSERT INTO eolCoord VALUES("+str(liste[k][0])+","+str(lat)+","+str(long)+")")

        elif int(liste[k][EPSG_Index])==27572:
            (x, y) = (liste[k][X_Index], liste[k][Y_Index])

            proj = pyproj.Transformer.from_crs(27572, 4326, always_xy=True)
            (long,lat)=proj.transform(x,y)
            c.execute("INSERT INTO eolCoord VALUES("+str(liste[k][0])+","+str(lat)+","+str(long)+")")

        elif int(liste[k][EPSG_Index]) == 4326:
            (x,y)=(liste[k][X_Index],liste[k][Y_Index])

            if "/" in x or "°" in x:
                (long, lat)=(degtodec(x),degtodec(y))
            else:
                (long,lat)=(x,y)
            c.execute("INSERT INTO eolCoord VALUES("+str(liste[k][0])+","+str(lat)+","+str(long)+")")

        elif int(liste[k][EPSG_Index]) != 0:
            proj = pyproj.Transformer.from_crs(int(liste[k][EPSG_Index]), 4326, always_xy=True)
            (x, y) = (liste[k][X_Index], liste[k][Y_Index])
            (long, lat) = proj.transform(x, y)
            c.execute("INSERT INTO eolCoord VALUES(" + str(liste[k][0]) + "," + str(lat) + "," + str(long) + ")")

        elif liste[k][XLamb93_Index] != 'Null':
            proj = pyproj.Transformer.from_crs(2154, 4326, always_xy=True)
            (x, y) = (liste[k][XLamb93_Index], liste[k][YLamb93_Index])
            (long, lat) = proj.transform(x, y)
            c.execute("INSERT INTO eolCoord VALUES(" + str(liste[k][0]) + "," + str(lat) + "," + str(long) + ")")
        elif liste[k][63] != 'Null' and liste[k][63] != 0:
            proj = pyproj.Transformer.from_crs(2154, 4326, always_xy=True)
            (x, y) = (liste[k][XIcpe_Index], liste[k][YIcpe_Index])
            (long, lat) = proj.transform(x, y)
            if lat<40:
                (x, y) = (liste[k][XCoord_ICPE], liste[k][YCoord_ICPE])
                (long, lat) = proj.transform(x, y)
            c.execute("INSERT INTO eolCoord VALUES(" + str(liste[k][0]) + "," + str(lat) + "," + str(long) + ")")
        else:
            if liste[k][1]!='Null':
                nomInstallation=urllib.parse.quote(str(liste[k][1])+" France")
            elif liste[k][4]!='Null' and not(liste[k][4][0] in ["0","1","2","3","4","5","6","7","8","9"]):
                nomInstallation=urllib.parse.quote(str(liste[k][4]))
            else:
                nomInstallation=urllib.parse.quote(retire_tiret(liste[k][80]))
            requeteRecherche=requests.get("https://geocode.search.hereapi.com/v1/geocode?q="+nomInstallation+"&apiKey=3d7kU6URqhCMvpHikh5hTJky1x9fyyu6FEGLy5T8cw4")
            try:
                rep = json.loads(requeteRecherche.content)
                rep=rep["items"][0]["position"]
                (long, lat) = (float(rep["lng"]),float(rep["lat"]))
            except:
                try:
                    nomInstallation=urllib.parse.quote(str(liste[k][1])[12:]+" France")
                    requeteRecherche=requests.get("https://geocode.search.hereapi.com/v1/geocode?q="+nomInstallation+"&apiKey=3d7kU6URqhCMvpHikh5hTJky1x9fyyu6FEGLy5T8cw4")
                    rep = json.loads(requeteRecherche.content)
                    rep=rep["items"][0]["position"]
                    (long, lat) = (float(rep["lng"]),float(rep["lat"]))
                except:
                    if liste[k][1]=="PARC EOLIEN D’ERELIA GROUP":
                        (lat, long) = (48.366953, 5.341819)
                    elif liste[k][1]=="PARC EOLIEN FE 10 NESLOISES IDEX GROUPE":
                        (lat,long)=(49.801953, 2.886144)
                    elif liste[k][1]=="PARC EOLIEN DU PLATEAU D’ANDIGNY 8":
                        (lat,long)=(50.002614, 3.543724)
                    elif liste[k][1]=="PARC EOLIEN SOLE DU VIEUX MOULIN":
                        (lat,long)=(49.843500, 2.801556)
                    else:
                        print(liste[k][0],liste[k][1])
                        (long, lat) = (0, 0)
                    pass
            if liste[k][1] == "PARC EOLIEN SOLE DU VIEUX MOULIN":
                (lat, long) = (49.843500, 2.801556)
            if lat<40 or lat>60:
                nc+=[liste[k][0]]
                print("ERREUR "+str(liste[k][0])+" !")
                print(nomInstallation)
                pu=2
                try:
                    pu=float(liste[k][24])
                except:
                    try:
                        pu=float(liste[k][41])
                    except:
                        pass
                if pu<10:
                    puissance_non_traite+=pu
                else:
                    puissance_non_traite+=2
            else:
                c.execute("INSERT INTO eolCoord VALUES(" + str(liste[k][0]) + "," + str(lat) + "," + str(long) + ")")

    print("Conversion terminée !\nSauvegarde...")
    conn.commit()
    conn.close()
    print("Terminé ! \n"+str(len(nc))+" éoliennes n'ont pas pu etre archivées pour une puissance de "+str(int(puissance_non_traite))+" MW")
    print(nc)

def production():
    def prod(w,p):
        if w<3:
            return 0
        elif w>20:
            return 0
        elif w>12:
            return p
        else:
            return p*(1.188/math.pi*math.atan(0.8*(w-6.4))+0.461)

    puissance_prod=0
    print("Connexion à la base de donnée...")
    conn=sqlite3.connect("eolienne.db")
    c=conn.cursor()
    c.execute("SELECT * FROM eolCoord")
    coord=c.fetchall()
    c.execute("SELECT * FROM eolFiltreGroup")
    groupEol=c.fetchall()
    print("Connecté !")
    print("Recherche des vents :")
    bar=progressbar.ProgressBar(max_value=len(groupEol))
    bar.start()
    for k in range(len(groupEol)):
        id=int(groupEol[k][3])
        p=float(groupEol[k][1])
        (lat,long)=(coord[id][1],coord[id][2])
        responseWeathAPI = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(long) + "&appid=8d783ab74b4115119149be5668440f2c")
        Weather = ast.literal_eval((responseWeathAPI.content).decode("UTF-8"))
        w=float(Weather["wind"]["speed"])+0.41
        productionparc=prod(w,p)
        #print([productionparc,w,str(p)+" MW",100*productionparc/p])
        puissance_prod+=productionparc
        bar.update(k)
    bar.finish()
    print("La puissance totale produite par les éoliennes est de "+str(puissance_prod)+"MW.")

    conn.close()

def duree_de_vie():
    print("Connexion à la base de donnée...")

    conn=sqlite3.connect("eolienne.db")
    c=conn.cursor()
    c.execute("DROP TABLE eolDate")
    c.execute('CREATE TABLE "eolDate" ("AnneeCrea" INTEGER,"Moicrea" INTEGER,"JourCrea" INTEGER,"AnneeFin" INTEGER,"MoisFin" INTEGER,"JourFin" INTEGER)')

    print("Connecté")

    bar=progressbar.ProgressBar(max_value=8520)

    mu,sigma1,sigma2=0,4,1
    crea = np.random.normal(mu, sigma1, 8520)
    crea=[2013+k for k in crea]

    duree_vie=np.random.normal(mu,sigma2,8520)
    duree_vie=[22+s for s in duree_vie]

    for k in range(len(crea)):
        bar.update(k)

        if crea[k]>2022:
            crea[k]=2022
        anneeC=int(crea[k])
        moisC=int((crea[k]-anneeC)*12)+1
        jourC=int(abs(((crea[k]-anneeC)*12-moisC))*30.4375)+1
        if duree_vie[k]<0:
            duree_vie[k]=0

        anneeF=int(duree_vie[k])
        moisF=int((duree_vie[k]-anneeF)*12)+1+moisC
        jourF=jourC+int(abs(((duree_vie[k]-anneeF)*12-moisF))*30.4375)+1

        if jourF > 31:
            jourF = jourF % 31 + 1
            moisF += 1
        if moisF>12:
            moisF=moisF%12+1
            anneeF+=1



        c.execute("INSERT INTO eolDate VALUES"+str((anneeC,moisC,jourC,anneeF+anneeC,moisF,jourF)))
    conn.commit()
    conn.close()

production()