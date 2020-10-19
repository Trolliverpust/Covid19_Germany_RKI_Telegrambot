import requests
import json, os
from datetime import datetime
import time
from gtts import gTTS


#---- Global tracking of cases and comparing to previous day
cases_yesterday = {}
deaths_yesterday = {}
firststart = True

#---- Start Telegram Part
bot_token = # YOUR BOT TOKEN HERE
chat_id = # YOUR CHAT ID HERE

def send_telegram(message):
    params = {"chat_id": chat_id, "text": message, "parse_mode":"markdown"}
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    server_message = requests.post(url, params=params)
    
    return server_message
#---- End Telegram Part
    
#---- Start Voiceoutput Part
def voice_output(text):
    tts = gTTS(text, lang='de')
    tts.save("voice.mp3")
    os.system("mpg321 voice.mp3")
#---- End Voiceoutput Part

#---- Start Dic-search Part
def find_county(county, data):
    for c in data["features"]:
        if c["properties"]["county"]==county:
            return c["properties"]
#---- End Dic-search Part


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
    #message += "Alle Angaben wie immer ohne Gewähr. Quelle: https://experience.arcgis.com/experience/478220a4c454480e823b17327b2bf1d4"
    return message

def send_text(county,data):
    message = data2text(county,data)
    print(message)
    send_telegram(message)

#---- End Data2Text Part


#---- Start Data2Text WITH VOICE Part
def data2textandvoice(county,data):
    global cases_yesterday, deaths_yesterday, firststart
    
    countydic = find_county(county, data)
    
    message = "*" + countydic["BEZ"] + " " + countydic['GEN'] + ": * \n"
    
    voiceline = "Hier sind die aktuellen COVID-19-Zahlen für "+countydic["BEZ"] + " " + countydic['GEN']+":"
    
    if not firststart: # Comparison of cases to previous day only possible if it is not the first day
        message += "Neue Infektionen: "+str(countydic["cases"]-cases_yesterday[county]) + "\n"
        message += "Neue Todesfälle: "+str(countydic["deaths"]-deaths_yesterday[county]) + "\n"
        
        voiceline += "Es sind "+str(countydic["cases"]-cases_yesterday[county]) + " neue Infektionen "
        voiceline += "und "+str(countydic["deaths"]-deaths_yesterday[county]) + " neue Todesfälle gemeldet worden."
    # Store case numbers for comparison next day
    cases_yesterday[county] = countydic["cases"]
    deaths_yesterday[county] = countydic["deaths"]
    
    message += "Fälle insgesamt: "+str(countydic["cases"]) + "\n"
    voiceline += "Insgesamt sind es "+str(countydic["cases"]) + "bestätigte Infektionen."
    
    message += "7-Tage-Inzidenz: "+str(round(countydic["cases7_per_100k"],1)) + "\n"
    voiceline += "Die Siebentageinzidenz liegt bei "+str(int(countydic["cases7_per_100k"]))+"Komma " + str(int((round(countydic["cases7_per_100k"],1)-(int(countydic["cases7_per_100k"])))*10))+ " ."
    
    message += "Todeszahlen insgesamt: "+str(countydic["deaths"]) + "\n"
    
    if str(countydic["deaths"]) == "1":
        voiceline += "Insgesamt gab es genau einen Todesfall"
    elif str(countydic["deaths"]) == "0":
        voiceline += "Insgesamt gab es gar keinen Todesfall"
    else:
        voiceline += "Insgesamt gab es"+str(countydic["deaths"]) + " Todesfälle"
    return [message,voiceline]


def send_text_and_voice(county,data):
    [message,voiceline] = data2textandvoice(county,data)
    print(message)
    send_telegram(message)
    voice_output(voiceline)
#---- End Data2Text WITH VOICE Part


#---- Start Endless Working Loop

messagetime = 12 # Anything between 0 and 22 is valid


done_for_today = False

while True:
    n = datetime.now().time()
    if messagetime == n.hour and not done_for_today:
        done_for_today = True
        
        data_from_today = get_data()
        
        # Replace this with the countys relevant to you
        #send_text("SK Kaiserslautern",data_from_today)
        send_text_and_voice("SK Kaiserslautern",data_from_today)
        #send_text("LK Kaiserslautern",data_from_today)
        send_text_and_voice("LK Kaiserslautern",data_from_today)
        
        firststart = False
        
    elif messagetime+1 == n.hour and done_for_today:
        done_for_today = False
    time.sleep(10)
