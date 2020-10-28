# COVID-19 Germany RKI Telegrambot
This repo contains a python script that helps you make a telegram bot which informs others about cases of COVID-19 based on data from the Robert Koch Institute.

Feel free to improve. Runs great on a Raspberry Pi Zero W which is also the target platform.

## Features
- Option to export data info to .mp3-Audio files (might be useful for people with visual impairment)
- Send Telegram Messages to a single user / chat group / channel
- Two timing options for sending messages: Send them every day at a set time or send them as soon as new data is available
- Save raw data for selected counties in a separate JSON-File

## Before you start
Enter your parameters in the `settings.py`-file. Then run in a terminal: `python3 main.py`. You may run several instances of the bot on the same machine. Make sure that every instance gets its own working directory. Otherwise the instances may access the same backup file which will result in wrong data.

## Basic requirements
- Host platform is permanently connected to the internet
- API-Token for Telegram Bot (german tutorial: https://statisquo.de/2020/08/21/telegram-bot-bauen-in-10-minuten-mit-python/)

## Requirements for broadcasting to a Telegram Channel
- Admin access to Telegram Channel
- Knowledge about Telegram Channel ID
- Bot in Telegram Channel with admin access

## Requirements for voice output
- Audio output hardware ready to go
- gtts package: sudo pip3 install gTTS
- mpg321 package installed (ask your default linux package manager)

## FAQ
- How do i change the settings of the scipt? \
&rarr; Edit the `settings.py`-file, then restart `main.py`
- Can i set multiple counties as options? \
&rarr; Yes. Just add them to the counties list in `settings.py`, then restart `main.py`.
- Does the script halt? \
&rarr; Not by design. To stop the script you have to abort the task manually. For permanent use on a Raspberry Pi it might be useful to use the tool "screen". This makes it possible to keep the script running even if you are logged out.
- The sent data is outdated. Where does this error come from? \
&rarr; The RKI database doesn't always give you the most recent data. You may have to send a request multiple times for a few minutes to get an current data record. The permanent update mode does not have this issue.
- Is it necessary to stay connected to the internet all the time? \
&rarr; For the mode that sends data as soon as it is available it is obviously necessary to be online all the time. If you just send data at a set time, it's just necessary to stay online 10 Minutes before. Say you want send data at 11 a.m., make sure the host system is online at 10:50 a.m. until the messages are sent. The 10 Minutes are there to buffer the information so it will be sent right on time.

## Known Issues
- When started, the script looks for a backup file. If the file is already there, it is assumed to be a backup file that contains at least data from the previous day. So if you run the script for a day, then turn it off for a several days and then restart it, the script does not calculate the new cases between this day and the day before, but the cases between this day and the day the backup file was last edited.
