# Edit this file to make everything fit your needs. Every "#####" is a placeholder.
# Once the main.py is started, any changes to these settings won't apply until
# the next restart of main.py


# First of all, what is your Bot's API-Token? Write it as String
token = #####

# What is the chat ID that your want to send the messages to? (private chats,
# groups and channels possible). Write it as integer. Also negative IDs are valid.
chat = #####

# What are your counties of interest? Enter their IDs as one list of Strings.
# Example: counties = ["SK Kaiserslautern","SK Karlsruhe"]
counties = #####

# In which mode should the bot operate? For sending data as soon as it is
# accessible, type "0". For sending data at a set time which you will enter in
# the step after, type "1"
mode = #####
        
# If you want to send the data every day at a full hour, enter the hour here
# (everything between 1 and 22 is valid, but RKI's numbers are mostly updated
# at 5 a.m.). If you don't use this mode, just type "1". Write the numbers
# as Integeres, so without ""
broadcast_time = #####

# Do you want your info to be spoken out loudly via a text to speech service?
# For Yes enter "1" for No enter "0"
voice = #####


def get_settings():
    global token, chat, counties, mode, broadcast_time,speech
    return[token,chat,counties,mode,broadcast_time,voice]
