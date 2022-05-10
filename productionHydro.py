import wptools
import csv
import sqlite3
import urllib
import progressbar
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

def rangement():
    def formattexte(s):
        sfin=''
        for k in range(len(s)):
            if s[k] in ['0','1','2','3','4','5','6','7','8','9','.']:
                sfin+=s[k]
            elif s[k]==",":
                sfin+="."
        return float(sfin)

    print("Conenxion à la base de donnée...")
    conn=sqlite3.connect("hydro.db")
    c=conn.cursor()
    try:
        c.execute('DROP TABLE hydro')
        c.execute("CREATE TABLE hydro(nom_riviere TEXT, nom_embouchure TEXT, bassin TEXT,longueur TEXT,H_max NUMERIC, H_min NUMERIC, debit NUMERIC)")
    except:
        c.execute("CREATE TABLE hydro(nom_riviere TEXT, nom_embouchure TEXT, bassin TEXT,longueur TEXT, H_max NUMERIC, H_min NUMERIC, debit NUMERIC)")
    print("Connecté !")
    print("Récupération du csv...")
    with open("hydro.csv",newline="") as f:
        reader=csv.reader(f)
        liste=list(reader)
    print("Récupéré")
    '''
    print("Conversion des noms...")
    bar=progressbar.ProgressBar(max_value=len(liste))
    accent = ['é', 'è', 'ê', 'à', 'â', 'û', 'ô', 'î', 'ï', 'ç']
    sans_accent = ['e', 'e', 'e', 'a', 'a', 'u', 'o', 'i', 'i', 'c']

    for i in range(len(liste)):
        bar.update(i)
        for j in range(len(accent)):
            liste[i][0]=liste[i][0].replace(accent[j],sans_accent[j])
            liste[i][1]=liste[i][1].replace(accent[j],sans_accent[j])
    bar.finish()
    print("Converti")
    '''
    liste[0] = ["Cours d'eau", ' Embouchure', ' Bassin', ' Longueur (km)', "H_max", "H_min", "Debit"]

    listenew=[]

    bar=progressbar.ProgressBar(max_value=len(liste))

    bar.start()
    for k in range(1,len(liste)):
        ajout=False
        try:
            search = wptools.page(liste[k][0], lang="fr", silent=True)
            infobox = search.get_parse().data
            infobox=infobox["infobox"]
            try:
                ajout=[infobox['source altitude'],infobox['embouchure altitude'],infobox["débit"]]
            except:
                try:
                    ajout = [infobox['source principale altitude'], infobox['embouchure altitude'], infobox["débit"]]
                except:
                    pass
        except:
            try:
                search = wptools.page(liste[k][0] + "_(rivière)", lang="fr", silent=True)
                infobox = search.get_parse().data
                infobox = infobox["infobox"]
                ajout = [infobox['source altitude'], infobox['confluence altitude'], infobox["débit"]]

            except:
                try:
                    search = wptools.page(liste[k][0] + "_(fleuve_français)", lang="fr", silent=True)
                    infobox = search.get_parse().data
                    infobox = infobox["infobox"]
                    ajout = [infobox['source altitude'], infobox['confluence altitude'], infobox["débit"]]

                except:
                    pass
        if ajout!=False:
            listenew+=[liste[k]+ajout]
        bar.update(k)

    bar=progressbar.ProgressBar(max_value=len(listenew))

    for k in range(len(listenew)):
        listenew[k][3]=formattexte(listenew[k][3])
        listenew[k][4]=formattexte(listenew[k][4])
        listenew[k][5]=formattexte(listenew[k][5])
        listenew[k][6]=formattexte(listenew[k][6])
        c.execute("INSERT INTO hydro VALUES"+str(tuple(listenew[k])))

    bar.finish()

    conn.commit()
    conn.close()

def production():
    conn=sqlite3.connect('hydro.db')
    c=conn.cursor()

    c.execute("SELECT * FROM hydro")
    liste=c.fetchall()

    p_tot=0
    g=9.8066
    rho=1000

    for k in range(len(liste)):
        Q,zf,z0=liste[k][6],liste[k][4],liste[k][5]
        H=zf-z0
        P=(g/H**2)*(zf**(3/2)+z0**(3/2))**2*rho*Q
        p_tot+=P
        #print(str(liste[k][0])+" produit "+str(P/1000)+" kW.")

    print("Les centrales hydroéléctriques produisent "+str(0.06*p_tot/(10**6))+" MW.")

    conn.close()
    return p_tot

prod=int(production())
print("Test"+str(prod))
socket.send_string(str(prod))
print("Test 2")