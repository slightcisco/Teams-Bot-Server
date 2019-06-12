import subprocess
import json
import os
import requests
import base64
from time import sleep
from requests.auth import HTTPBasicAuth

def bashCommand(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output
print("CHECKING DEPENDENCIES INSTALLED")
pip_list = bashCommand("pip list")
if "Flask" not in pip_list:
    print("Flask is not installed, would you like to install now? ")
    inp = str(raw_input("[Y/N]"))
    if inp == "n" or inp == "N":
        print("Quitting due to requirements failure")
        quit()
    else:
        print("Installing flask")
        bashCommand("pip install flask")
if "webexteamssdk" not in pip_list:
    print("Webex Teams SDK is not installed, would you like to install now? ")
    inp = str(raw_input("[Y/N]"))
    if inp == "n" or inp == "N":
        print("Quitting due to requirements failure")
        quit()
    else:
        print("Installing webex teams sdk")
        bashCommand("pip install webexteamssdk")
print ("Dependencies all installed")
ngrok_running = False
while ngrok_running == False:
    running_jobs = bashCommand("ps aux")
    if "ngrok http 5000" in running_jobs:
        ngrok_running = True
        print("NGROK is running correctly")
    else:
        print("NGROK is either not running or not running correctly")
        print("Please open a new terminal type: ngrok http 5000")
        raw_input("Press enter to continue.....")
print("Getting URL")
json_arg = bashCommand("curl -s localhost:4040/api/tunnels")
json_arg = json.loads(json_arg)
print(len(json_arg['tunnels']))
NGROK_url = json_arg['tunnels'][0]['public_url']
print(NGROK_url)

try:
    f = open('./access.tkn', 'r')
    token = f.read()
    token_empty = False
    print("TOKEN FOUND IN access.tkn")
    f.close()
except :
    token_empty = True
    token = ""
    f = open('./access.tkn', 'w')
    print("No token was found")
while token_empty:
    print("Navigate to developer.webex.com and create an account/login")
    print("Click your profile in the top right, click 'My Webex Teams Apps' and create a new bot")
    token = raw_input("Please enter the ACCESS_TOKEN for your bot: ")
    if token == "":
        print("Please enter a token, cannot leave this blank")
    else:
        f.write(token)
        token_empty = False
try:
    f = open('./AWX.pass', 'r')
    awx = f.read()
    awx_empty = False
    print("TOKEN FOUND IN awx.pass")
    f.close()
except :
    awx_empty = True
    awx = ""
    f = open('./AWX.pass', 'w')
    print("No token was found")
while awx_empty:
    awx_ip = raw_input("Please enter the IP or domain name for your AWX: ")
    awx_user = raw_input("Please enter the username for your AWX: ")
    awx_pass = raw_input("Please enter the password for your AWX: ")
    awx_token = awx_user + ":" + awx_pass
    awx_token = awx_token.encode("UTF-8")
    awx_token = base64.b64encode(awx_token)

    print(awx_token)
    if awx_token == "":
        print("Please enter a token, cannot leave this blank")
    else:
        f.write(awx_token + "\n" + awx_ip)
        awx_empty = False

try:
    f = open('./apic.creds', 'r')
    creds = f.read()
    creds_empty = False
    print("APIC CREDENTIALS FOUND IN apic.creds")
    f.close()
except :
    creds_empty = True
    creds = ""
    f = open('./apic.creds', 'w')
    print("No creds were found")
while creds_empty:
    apic_ip = raw_input("Please enter the IP address (or domain name) for your APIC: ")
    apic_user = raw_input("Please enter the username for your APIC: ")
    apic_pass = raw_input("Please enter the password for your APIC: ")
    if apic_ip == "" or apic_pass == "" or apic_pass == "":
        print("Please enter a creds, cannot leave this blank")
    else:
        return_str = str(apic_ip + "\n" + apic_user + "\n" + apic_pass)
        f.write(return_str)
        creds_empty = False

URL = "https://api.ciscospark.com/v1/webhooks"

print( "TEAMS TOKEN: " + str(token))
HEADERS = {
'Authorization':'Bearer '+str(token)
}

DATA = {
'name': 'NGROK created automatically',
'targetUrl': NGROK_url,
'resource': 'all',
'event': 'all'
}
webhook_list = requests.get(url = "https://api.ciscospark.com/v1/webhooks", headers = HEADERS)
webhook_list = json.loads(webhook_list.text)
print("_____WEBHOOK LIST BELOW:_____")
print(webhook_list)
webhook_items = webhook_list['items']
for i in range(len(webhook_items)):
    if webhook_items[i]['name'] == "NGROK created automatically":
        delete_request = requests.delete(url = "https://api.ciscospark.com/v1/webhooks/" + str(webhook_items[i]['id']), headers = HEADERS)

r = requests.post(url = URL, headers = HEADERS, data = DATA)

print("New webhook created!")
os.environ['WEBEX_TEAMS_ACCESS_TOKEN'] = token
os.environ['FLASK_APP'] = "bot_server.py"
bashCommand("python -m flask run --host=0.0.0.0")

