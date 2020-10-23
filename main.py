import settings
import requests
import os
import json
from datetime import datetime
import time
from gtts import gTTS

# Import settings
[bot_token,chat_id,counties,mode,broadcast_time,voice] = settings.get_settings()

update_interval = 300 #Seconds

# Global tracking of cases and comparing to previous day
cases_yesterday = {}
deaths_yesterday = {}
firststart = False

# Try to restore Data from Backup File

filename = "Backup_"
for l in counties:
    filename += l.replace(" ", "_")
    filename += "_"
filename += ".json"

try:
    with open(filename, 'r') as backupfile:
        data = backupfile.readlines()
        if len(data)<=1:
            last_backup = json.loads(data[0])
        else:
            last_backup = json.loads(data[-1])
        
        for c in counties:
            cases_yesterday[c] = last_backup[c]["cases"]
            deaths_yesterday[c] = last_backup[c]["deaths"]
except IOError:
    firststart = True
    print("Couldn't restore data from backup file, creating a new one")


def send_telegram(message):
    global chat_id, bot_token
    """
    Sends the str "message" to the set Chat ID
    """
    params = {"chat_id": chat_id, "text": message, "parse_mode":"markdown"}
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    server_message = requests.post(url, params=params)

    return server_message


def voice_output(text):
    """
    Says a given text out loud.
    """
    tts = gTTS(text, lang='de')
    tts.save("voice.mp3")
    os.system("mpg321 voice.mp3")


def find_county(county, data):
    """
    Extacts the relevant Data-Dictionary for a certain county from the entire JSON-Dataset sent by the server
    """
    for c in data["features"]:
        if c["properties"]["county"]==county:
            return c["properties"]


def get_data():
    global counties
    """
    Request data from server and convert it to list of countydics
    """
    url = "https://opendata.arcgis.com/datasets/917fc37a709542548cc3be077a786c17_0.geojson"

    request = requests.get(url)
    server_answer = json.loads(request.content)
    
    # In our tests, loading the JSON-Files can make up to 100 MB RAM-Usage. So for performance
    # reasons, the relevant data gets extracted as soon as possible.
    
    data_compact = []
    for c in counties:
        data_compact.append([c,find_county(c,server_answer)])

    return data_compact


def data2text(countytuple):
    """
    Takes a info tuple for one single county, returns a readable string with an assembled message
    """
    global cases_yesterday, deaths_yesterday, firststart
    
    countydic = countytuple[1]
    
    message = "*" + countydic["BEZ"] + " " + countydic['GEN'] + ": * \n"

    if not firststart: # Comparison of cases to previous day only possible if it is not the first day
        message += "Neue Infektionen: "+str(countydic["cases"]-cases_yesterday[countytuple[0]]) + "\n"
        message += "Neue Todesfälle: "+str(countydic["deaths"]-deaths_yesterday[countytuple[0]]) + "\n"

    # Store case numbers for comparison next day
    cases_yesterday[countytuple[0]] = countydic["cases"]
    deaths_yesterday[countytuple[0]] = countydic["deaths"]

    message += "Fälle insgesamt: "+str(countydic["cases"]) + "\n"
    message += "7-Tage-Inzidenz: "+str(round(countydic["cases7_per_100k"],1)).replace(".", ",") + "\n"
    message += "Todeszahlen insgesamt: "+str(countydic["deaths"]) + "\n"
    message += "Stand: "+countydic["last_update"] + "\n"
    
    return message


def send_text(countytuple):
    message = data2text(countytuple)
    # print(message)
    send_telegram(message)


def data2textandvoice(countytuple):
    """
    Takes data set and county setting, returns a readable string with an
    assembled message and outputs the data via a connected speaker
    """
    
    countydic = countytuple[1]
    global cases_yesterday, deaths_yesterday, firststart
    
    message = "*" + countydic["BEZ"] + " " + countydic['GEN'] + ": * \n"

    voiceline = "Hier sind die aktuellen COVID-19-Zahlen für "+countydic["BEZ"] + " " + countydic['GEN']+":"
    
    if not firststart: # Comparison of cases to previous day only possible if it is not the first day
        message += "Neue Infektionen: "+str(countydic["cases"]-cases_yesterday[countytuple[0]]) + "\n"
        message += "Neue Todesfälle: "+str(countydic["deaths"]-deaths_yesterday[countytuple[0]]) + "\n"
        
        voiceline += "Es sind "+str(countydic["cases"]-cases_yesterday[countytuple[0]]) + " neue Infektionen "
        voiceline += "und "+str(countydic["deaths"]-deaths_yesterday[countytuple[0]]) + " neue Todesfälle gemeldet worden."
    # Store case numbers for comparison next day
    cases_yesterday[countytuple[0]] = countydic["cases"]
    deaths_yesterday[countytuple[0]] = countydic["deaths"]
    
    message += "Fälle insgesamt: "+str(countydic["cases"]) + "\n"
    voiceline += "Insgesamt sind es "+str(countydic["cases"]) + "bestätigte Infektionen."
    
    message += "7-Tage-Inzidenz: "+str(round(countydic["cases7_per_100k"],1)).replace(".", ",") + "\n"
    voiceline += "Die Siebentageinzidenz liegt bei " + str(int((round(countydic["cases7_per_100k"],1)))).replace(".", ",") + " \n"
    
    message += "Todeszahlen insgesamt: "+str(countydic["deaths"]) + "\n"
    message += "Stand: "+countydic["last_update"] + "\n"
    
    if str(countydic["deaths"]) == "1":
        voiceline += "Insgesamt gab es genau einen Todesfall"
    elif str(countydic["deaths"]) == "0":
        voiceline += "Insgesamt gab es gar keinen Todesfall"
    else:
        voiceline += "Insgesamt gab es"+str(countydic["deaths"]) + " Todesfälle"
    return [message,voiceline]


def send_text_and_voice(countytuple):
    [message,voiceline] = data2textandvoice(countytuple)
    # print(message)
    send_telegram(message)
    voice_output(voiceline)
    

def broadcast(countytuples):
    """
    Initiates broadcasting the data and writes it tot backup file
    """
    global speech, filename
    
    todays_backup = {}
    
    for cd in countytuples:
        
        todays_backup[cd[0]] = cd[1]
        
        if voice == 1 or voice == "1":
            send_text_and_voice(cd)
        else:
            send_text(cd)
    
    with open(filename,"a") as backupfile:
        json.dump(todays_backup, backupfile)
        backupfile.write('\n')

if mode == "0" or mode == 0:
    # Send new data as soon as possible
    
    latest_relevant_data = get_data()
    broadcast(latest_relevant_data)
    last_sent_update = latest_relevant_data[0][1]["last_update"]
    firststart = False
    
    while True:
        most_recent_data = get_data()
        recent_update = most_recent_data[0][1]["last_update"]
        
        if recent_update != last_sent_update:
            latest_relevant_data = most_recent_data
            broadcast(latest_relevant_data)
            last_sent_update = latest_relevant_data[0][1]["last_update"]
            print("New Update!")
            print(datetime.now().time())
            print("---")
        else:
            print("No new update")
            print(datetime.now().time())
        time.sleep(update_interval)
    
elif mode == "1" or mode == 1:
    # Send new data every day at the same time
    
    done_for_today = False
    got_todays_data = False
    data_from_today = None
    
    while True:
        n = datetime.now().time()
        
        # Get data 10 Minutes before it's time to send so the CPU can process it on time
        if n.hour == broadcast_time-1 and n.minute >= 50 and not done_for_today and not got_todays_data:
            print("Reaching out to server...")
            data_from_today = get_data()
            got_todays_data = True
            print("Okay.")
        
        if broadcast_time == n.hour and not done_for_today and got_todays_data:
            done_for_today = True
            
            broadcast(data_from_today)
            
            firststart = False
        
        elif broadcast_time == n.hour and not done_for_today and not got_todays_data:
            print("There won't be an update today unless you give the timer + 1 hour")
        
        elif broadcast_time+1 == n.hour and done_for_today:
            done_for_today = False
            got_todays_data = False
        time.sleep(10)
else:
    raise ValueError("Error while applying settings: Couldn't read mode setting. Enter 0 or 1 as value for mode in settings.py")
