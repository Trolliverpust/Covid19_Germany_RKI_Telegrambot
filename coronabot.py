import requests
import json
from datetime import datetime
import time

# County Kaiserslautern is selected for showcase reasons

#---- Global tracking of cases and comparing to previous day
cases_yesterday = {}
deaths_yesterday = {}
firststart = True

#---- Start Telegram Part
bot_token = #YOUR TOKEN HERE
chat_id = #YOUR CHANNEL ID HERE

def send_telegram(message):
    params = {"chat_id": chat_id, "text": message, "parse_mode":"markdown"}
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    message = requests.post(url, params=params)
    
    return message
#---- End Telegram Part


#---- Start Data Recieving Part
def get_data():
    # unfiltered
    # url = "https://opendata.arcgis.com/datasets/917fc37a709542548cc3be077a786c17_0.geojson"
    # KL only (smaller, but more specific)
    url = "https://opendata.arcgis.com/datasets/917fc37a709542548cc3be077a786c17_0.geojson?where=GEN%20%3D%20%27Kaiserslautern%27"
    
    request = requests.get(url)
    server_answer = json.loads(request.content)
    
    return server_answer
#---- End Data Recieving Part


#---- Start Data2Text Part
def find_county(county, data):
    for c in data["features"]:
        if c["properties"]["county"]==county:
            return c["properties"]
        

def data2text(county,data):
    global cases_yesterday, deaths_yesterday, firststart
    
    countydic = find_county(county, data)
    
    message = "*" + countydic["BEZ"] + " " + countydic['GEN'] + ": * \n"
    
    if not firststart: # Comparison of cases to previous day only possible if it is not the first day
        message += "Neue Infektionen: "+str(countydic["cases"]-cases_yesterday[county]) + "\n"
        message += "Neue Todesfälle: "+str(countydic["deaths"]-deaths_yesterday[county]) + "\n"
    
    # Store case numbers for comparison next day
    cases_yesterday[county] = countydic["cases"]
    deaths_yesterday[county] = countydic["deaths"]
    
    message += "Fälle insgesamt: "+str(countydic["cases"]) + "\n"
    message += "7-Tage-Inzidenz: "+str(round(countydic["cases7_per_100k"],1)) + "\n"
    message += "Todeszahlen insgesamt: "+str(countydic["deaths"]) + "\n"
    message += "----"+ "\n"
    #message += "Alle Angaben wie immer ohne Gewähr. Quelle: https://experience.arcgis.com/experience/478220a4c454480e823b17327b2bf1d4"
    return message

def send_text(county,data):
    message = data2text(county,data)
    print(message)
    send_telegram(message)

#---- End Data2Text Part


#---- Start Endless Working Loop

messagetime = 12 # Anything between 0 and 22 is valid

done_for_today = False

while True:
    n = datetime.now().time()
    if messagetime == n.hour and not done_for_today:
        done_for_today = True
        
        tagesdaten = get_data()
        
        # Replace this with the countys relevant to you
        send_text("SK Kaiserslautern",tagesdaten)
        send_text("LK Kaiserslautern",tagesdaten)
        
        firststart = False
        
    elif messagetime+1 == n.hour and done_for_today:
        done_for_today = False
    time.sleep(10)
