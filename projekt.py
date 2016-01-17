import os
import requests
import sys
import re
import csv


leta = [i for i in range(1968,2016)]
regularni1 = r'href="(/en/scores/archive/\w+-?\w*/\d+/\d+/results)"'
regularni2 = r'href=("/en/tournaments/\w+-?\w+?-?\w+?-?\w+?-?\w+?/\d+/\d+/match-stats/\w\d+/\w\d+/live/\w+\d+/match-stats")>'
regularni3 = r'(?:\d+ ){2,5}'
def shrani(url, ime_datoteke, vsili_prenos=False):
    '''Vsebino strani na danem naslovu shrani v datoteko z danim imenom.'''
    try:
        print('Shranjujem {}...'.format(url), end='')
        sys.stdout.flush()
        if os.path.isfile(ime_datoteke) and not vsili_prenos:
            print('shranjeno že od prej!')
            return
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('stran ne obstaja!')
    imenik = os.path.dirname(ime_datoteke)
    if imenik:
        os.makedirs(imenik, exist_ok=True)
    with open(ime_datoteke, 'w') as datoteka:
        datoteka.write(r.text)
        print('shranjeno!')


def vsebina_datoteke(ime_datoteke):
    '''Vrne niz z vsebino datoteke z danim imenom.'''
    with open(ime_datoteke) as datoteka:
        vsebina = datoteka.read()
    return vsebina


def datoteke(imenik):
    '''Vrne imena vseh datotek v danem imeniku skupaj z imenom imenika.'''
    return [os.path.join(imenik, datoteka) for datoteka in os.listdir(imenik)]

def najdi(datoteka,regularni):
    return re.findall(regularni, datoteka, re.DOTALL)


def pripravi_imenik(ime_datoteke):
    '''Če še ne obstaja, pripravi prazen imenik za dano datoteko.'''
    imenik = os.path.dirname(ime_datoteke)
    if imenik:
        os.makedirs(imenik, exist_ok=True)



def zapisi_tabelo(slovarji, imena_polj, ime_datoteke):
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w') as csv_dat:
        writer = csv.DictWriter(csv_dat, fieldnames=imena_polj)
        writer.writeheader()
        for slovar in slovarji:
            writer.writerow(slovar)

def vsota_rezultat(seznam):
    pomozn_sez = []
    for el in seznam:
        pom = el.split()
        for el in pom:
            if len(el) <= 2:
                vsota = 0
                for stevilo in el:
                    vsota += int(stevilo)
                pomozn_sez.append(vsota)
            elif len(el) == 4:
                rez1 = el[:2]
                rez2 = el[2:]
                vsota = int(rez1) + int(rez2)
                pomozn_sez.append(vsota)
            else:
                if int(el[:2]) - int(el[2]) == 2:
                    rez1 = el[:2]
                    rez2 = el[2]
                    vsota = int(rez1) + int(rez2)
                    pomozn_sez.append(vsota)
                else:
                    rez1 = el[:1]
                    rez2 = el[1:]
                    vsota = int(rez1) + int(rez2)
                    pomozn_sez.append(vsota)

    return pomozn_sez

for leto in leta:
    url = "http://www.atpworldtour.com"
    shrani("http://www.atpworldtour.com/en/scores/results-archive?year={}".format(str(leto)),"leto {}.txt".format(str(leto)))
    sez = najdi(vsebina_datoteke("leto {}.txt".format(leto)),regularni1)
    for el in sez:
        pot = re.findall(r"en/scores/archive/(?P<turnir>\w+-?\w+)/(?P<neki>\d+)/(?P<leto>\d+)",el)
        shrani(url + el, r"C:/Users/Miha/Desktop/projekt/turnirji" + r"/" + pot[0][0] + r"/" + pot[0][1] + r"/"  + pot[0][2] + r"/" + "/results.txt")
        
podatki, igralci_slovar, turnirji = {}, {}, {}
indeks = 0
indeks_igralca = 0
indeks_turnirja = 0
for subdir, dirs, files in os.walk(r"C:/Users/Miha/Desktop/projekt/turnirji/"):
    for file in files:
        b = os.path.join(subdir, file)
        ime = re.findall(r"turnirji/(.*?)\\",str(b),re.DOTALL)[0]
        leto = re.findall(r"\d+\d+",str(b),re.DOTALL)[1]
        podlaga_s = re.findall(r'\s(Grass|Hard|Clay|Carpet)\s', vsebina_datoteke(b), re.DOTALL)
        podlaga = podlaga_s[0].strip()
        igralci = re.findall(r'<td class="day-table-name">\s+.*?>(.*?)</a>', vsebina_datoteke(b), re.DOTALL)
        for igralec in igralci:
            if igralec in igralci_slovar:
                pass
            else:
                igralci_slovar[igralec] = {"ime":igralec,"id":indeks_igralca}
                indeks_igralca += 1
        rezultat = re.findall(r'(?:\d+ ){2,5}', vsebina_datoteke(b), re.DOTALL)
        stevec = 0
        for igra in rezultat:
            if stevec < (len(igralci) - 1):
                if ime in turnirji:
                    podatki[indeks]={"turnir":turnirji[ime]["id"],"leto":leto,"st_iger":sum(vsota_rezultat(igra)),"podlaga":podlaga,"zmagovalec":igralci_slovar[igralci[stevec]]["id"],"porazenec":igralci_slovar[igralci[stevec + 1]]["id"]}
                    indeks += 1
                    stevec += 2
                else:
                    turnirji[ime]={"ime":ime,"id": indeks_turnirja}
                    indeks_turnirja += 1
                    podatki[indeks]={"turnir":turnirji[ime]["id"],"leto":leto,"st_iger":sum(vsota_rezultat(igra)),"podlaga":podlaga,"zmagovalec":igralci_slovar[igralci[stevec]]["id"],"porazenec":igralci_slovar[igralci[stevec + 1]]["id"]}
                    indeks += 1
                    stevec += 2


    
zapisi_tabelo(podatki.values(), ["turnir","leto","podlaga","st_iger","zmagovalec","porazenec"], "podatki.csv")
zapisi_tabelo(turnirji.values(), ["id","ime"], "turnirji.csv")
zapisi_tabelo(igralci_slovar.values(), ["id","ime"], "igralci.csv")