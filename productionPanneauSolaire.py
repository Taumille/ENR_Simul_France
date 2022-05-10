import sqlite3
import progressbar
import requests
import json
import time
import math
import matplotlib.pyplot as plt
import numpy as np

def traitement_donnée():
    def changeNombreLong(nb):
        nb=str(nb)
        if len(nb)>=3 or nb[0]!="0":
            result=""
            k=0
            result+=nb[k]+"."
            k+=1
            for i in range(k,len(nb)):
                if nb[i]!=".":
                    result+=nb[i]
            try:
                return float(result)
            except:
                print("ERREUR long POUR "+nb)
        else:
            return float(nb)

    def changeNombreLat(nb):
        nb=str(nb)
        if len(nb)>=3 and nb[0]!="0":
            result=""
            k=0
            if nb[0]=="-":
                k+=1
                result+="-"
            result+=nb[k]+nb[k+1]+"."
            k+=2
            for i in range(k,len(nb)):
                if nb[i]!=".":
                    result+=nb[i]
            try:
                return float(result)
            except:
                print("ERREUR lat POUR "+nb)
        else:
            return float(nb)

    print("Connexion à la base de donnée des villes:")
    conn=sqlite3.connect("villes.db")
    c=conn.cursor()
    c.execute("SELECT * FROM villes")
    liste=c.fetchall()
    print("Connecté")

    k=0
    bar=progressbar.ProgressBar(max_value=len(liste))
    for elem in liste:
        e=list(elem)
        e[8]=changeNombreLong(e[8])
        e[9]=changeNombreLat(e[9])
        e=tuple(e)
        if len(str(e[1]))<=2:
            c.execute("INSERT INTO villesmod VALUES"+str(e))
        k+=1
        bar.update(k)
    bar.finish()
    conn.commit()
    conn.close()

def prod():
    print("Connexion à la base de donnée des villes:")
    conn=sqlite3.connect("villes.db")
    c=conn.cursor()
    c.execute("SELECT * FROM villesmod")
    liste=c.fetchall()
    print("Connecté")

    c.execute("DROP TABLE villes_solaires")
    c.execute('CREATE TABLE "villes_solaires" ("nom" TEXT,"surface" NUMERIC,"latitude" NUMERIC,"longitude" NUMERIC)')

    phi=((time.time()%86400+2*3600)-23160)/54840
    R_0=990-30
    surface_couverte=10/100

    P_tot=0
    S_tot=0

    compteur=0

    bar=progressbar.ProgressBar(max_value=len(liste))

    bar.start()
    for k in range(len(liste)):
        #bar.update(k)
        if liste[k][6]>400 and str(liste[k][1]) in ["6","83","84","13","4","30","34","66","2A","2B"] and math.sin(phi)>0:
            compteur+=1
            s=liste[k][7]*1000000
            (long,lat)=(liste[k][8],liste[k][9])
            responseWeathAPI = requests.get("https://api.openweathermap.org/data/2.5/weather?lat="+str(lat)+"&lon="+str(long)+"&appid=8d783ab74b4115119149be5668440f2c")
            responseWeathAPI=json.loads(responseWeathAPI.content)
            cloudiness=responseWeathAPI["clouds"]["all"]
            P_prod=0.4*(R_0*(1-0.75*(cloudiness/100)**3.4))*s*surface_couverte*math.sin(phi)
            P_tot+=P_prod
            S_tot+=s*surface_couverte
            print("Dans la ville de "+str(liste[k][3])+" "+str(P_prod/1000000)+" MW sont produits sur "+str(s*surface_couverte/1000000)+" km2.")

    bar.finish()
    print("En France " + str(P_tot / 1000000000) + " GW sont produits sur " + str(S_tot/1000000)+" km2")
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




prod()
