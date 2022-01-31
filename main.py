import requests
from bs4 import BeautifulSoup
import csv
import re
import time
from difflib import SequenceMatcher

urlList = ["https://chanson-francaise.tiuls.fr/1.2.3", \
"https://chanson-francaise.tiuls.fr/adi","https://chanson-francaise.tiuls.fr/amo", \
"https://chanson-francaise.tiuls.fr/auj","https://chanson-francaise.tiuls.fr/bel", \
"https://chanson-francaise.tiuls.fr/bra","https://chanson-francaise.tiuls.fr/cap", \
"https://chanson-francaise.tiuls.fr/c%27es","https://chanson-francaise.tiuls.fr/cha", \
"https://chanson-francaise.tiuls.fr/com","https://chanson-francaise.tiuls.fr/dan", \
"https://chanson-francaise.tiuls.fr/des","https://chanson-francaise.tiuls.fr/don", \
"https://chanson-francaise.tiuls.fr/ell","https://chanson-francaise.tiuls.fr/et-j", \
"https://chanson-francaise.tiuls.fr/fem","https://chanson-francaise.tiuls.fr/gim", \
"https://chanson-francaise.tiuls.fr/his","https://chanson-francaise.tiuls.fr/il-n", \
"https://chanson-francaise.tiuls.fr/j%27ai","https://chanson-francaise.tiuls.fr/je-c", \
"https://chanson-francaise.tiuls.fr/je-s","https://chanson-francaise.tiuls.fr/j%27me", \
"https://chanson-francaise.tiuls.fr/l%27am","https://chanson-francaise.tiuls.fr/la-c", \
"https://chanson-francaise.tiuls.fr/la-g","https://chanson-francaise.tiuls.fr/la-p", \
"https://chanson-francaise.tiuls.fr/la-v","https://chanson-francaise.tiuls.fr/l%27am", \
"https://chanson-francaise.tiuls.fr/l%27amo","https://chanson-francaise.tiuls.fr/le-c", \
"https://chanson-francaise.tiuls.fr/le-l","https://chanson-francaise.tiuls.fr/le-p", \
"https://chanson-francaise.tiuls.fr/le-v","https://chanson-francaise.tiuls.fr/les-c", \
"https://chanson-francaise.tiuls.fr/les-m","https://chanson-francaise.tiuls.fr/les-y" \
"https://chanson-francaise.tiuls.fr/lon","https://chanson-francaise.tiuls.fr/mac", \
"https://chanson-francaise.tiuls.fr/mar","https://chanson-francaise.tiuls.fr/min", \
"https://chanson-francaise.tiuls.fr/mon","https://chanson-francaise.tiuls.fr/ne-s", \
"https://chanson-francaise.tiuls.fr/o-se","https://chanson-francaise.tiuls.fr/ou-e", \
"https://chanson-francaise.tiuls.fr/par","https://chanson-francaise.tiuls.fr/pic", \
"https://chanson-francaise.tiuls.fr/pou","https://chanson-francaise.tiuls.fr/qua", \
"https://chanson-francaise.tiuls.fr/ram","https://chanson-francaise.tiuls.fr/roc", \
"https://chanson-francaise.tiuls.fr/sat","https://chanson-francaise.tiuls.fr/si-t", \
"https://chanson-francaise.tiuls.fr/sou","https://chanson-francaise.tiuls.fr/ta,-q", \
"https://chanson-francaise.tiuls.fr/thi","https://chanson-francaise.tiuls.fr/tou", \
"https://chanson-francaise.tiuls.fr/tu-n","https://chanson-francaise.tiuls.fr/un-p", \
"https://chanson-francaise.tiuls.fr/ven","https://chanson-francaise.tiuls.fr/voy"]

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# to do : refaire récupération chansons depuis le site 
def getSongs():
    response = requests.get("https://chanson-francaise.tiuls.fr/1.2.3")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    tmp = []
    tds = soup.find("table",attrs={"border":"0","cellpadding":"0","cellspacing":"0","style":"border-collapse: collapse; width: 340pt;","width":"452"})
    tmp_td_children = tds.findChildren("td")
    
    for td_child in tmp_td_children:
        tmp_data = td_child.get_text().replace("\n"," ")
        tmp += [tmp_data]
    
    tuples = [tmp[x:x+3] for x in range(0, len(tmp),3)]
    
    with open('test.csv', 'a', newline='', encoding ='utf-8') as csvfile:
        for tuple in tuples:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(tuple)

# récupère les urls associés à chaque musique
def getSongsUrl():

    with open('originalData.csv', newline='', encoding ='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            # reconstruction du format des titres depuis l'API pour les comparer (voir similarity)
            query = " by ".join(row[0:2])
            
            url = "https://api.genius.com/search?q=" + query
            payload = {"access_token":"COuf26_ZZcSurLiwGwFrcb3tnZotE3kcNAR1gUz9ffI-bwlEwt_j2kt8NU79qv2R"}

            resp = requests.get(url, params=payload)
            data = resp.json()

            # si pas de résulats suite à la recherche, continue
            if len(data["response"]["hits"]) > 0:   
                data = data["response"]["hits"][0]
            else: 
                continue
            
            # récupération url et titre depuis l'API
            geniusUrl = data["result"]["url"]
            title = data["result"]["full_title"]

            # comparaison titre scrapé et titre API
            similarity = similar(title,query)
            if similarity < 0.8:
                continue

            row += [geniusUrl]

            # enrigistre la data dans un nouveau csv en ajoutant le lien à la ligne
            with open('geniusData.csv', 'a', newline='', encoding ='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=",")
                writer.writerow(row)


# get lyrics for genius urls     
def getLyrics():
    
    with open('geniusData.csv', newline='', encoding ='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            response = requests.get(row[-1])

            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            lyrics = soup.find("div",class_="SongPageGriddesktop__TwoColumn-sc-1px5b71-1 hfRKjb Lyrics__Root-sc-1ynbvzw-1 kZmmHP")
            
            # cleanup des lyrics si elles existent dans la page
            if lyrics:
                lyrics = lyrics.get_text(separator="\n")
                lyrics = re.sub(r'(?m)^,|[\[\()].*?[\)\]]|.x\d+|(?m)^\d+|\bEmbed\b|\bCopy\b|(Share.URL)|/g', '', lyrics)
                lyrics = lyrics.splitlines()
                
                try:
                    lyrics = list(filter(None, lyrics))
                except ValueError:
                    pass

                lyrics.remove(' ') if ' ' in lyrics else None
                lyrics = '. '.join(lyrics)
            else: 
                continue

            row += [lyrics]

            # ajout des lyrics dans un nouveau dataset
            with open('finalData.csv', 'a', newline='', encoding ='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=",")
                writer.writerow(row)

            # timeout pour ne pas se faire ratelimit
            time.sleep(0.1)

getSongs()
getSongsUrl()
getLyrics()

