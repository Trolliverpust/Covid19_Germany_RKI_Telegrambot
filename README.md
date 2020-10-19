# Covid19 Germany RKI Telegrambot
This repo contains a python script that helps you make a telegram bot which informs others about cases of Covid-19 based on data from the Robert Koch Institute.

Feel free to improve. Runs great on a Raspberry Pi Zero W which is also the target platform.

Basic requirements:
- Telegram Channel
- Bot in Telegram Channel with Admin Access

Requirements for voice output:
- Audio output hardware ready to go
- gtts package: sudo pip3 install gTTS
- mpg321 package installed (ask your default linux package manager)
