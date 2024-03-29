import socket
import time
import requests
import json
from flask import Flask
from flask import request
from webexteamssdk import WebexTeamsAPI, Webhook
from base64 import b64encode


api = WebexTeamsAPI()


# Find all rooms that have 'webexteamssdk Demo' in their title
all_rooms = api.rooms.list()
demo_room = [room for room in all_rooms if 'webexteamssdk Demo' in room.title]

app = Flask(__name__)

def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True

def getIP(message):
    pre, preTwo, ip = message.split(" ")
    if(is_valid_ipv4_address(ip)):
        print("IP IS" + str(ip))
        return ip
    else:
        return "not_valid"


@app.route('/', methods=['POST'])
def messageHandling():
    f = open('./apic.creds', 'r')
    creds = f.read()
    f.close()
    creds = creds.split("\n")
    APIC_ADDR = creds[0]
    APIC_USER = creds[1]
    APIC_PASS = creds[2]

    f = open('./access.tkn', 'r')
    bot_token = f.read()
    f.close()

    f = open('./AWX.pass', 'r')
    contents = f.read()
    contents = contents.split('\n')
    awx_token = contents[0]
    awx_IP = contents[1]
    f.close()

    print(awx_token)
    json_data = request.data
    # Create a Webhook object from the JSON data
    webhook_obj = Webhook(json_data)
    # Get the room details
    room = api.rooms.get(webhook_obj.data.roomId)
    # Get the message details ATM messages.get is bad, and i think it has delay while getting group chat messages
    message = api.messages.get(webhook_obj.data.id)
    # Get the sender's details
    person = api.people.get(message.personId)
    me = api.people.me()

    print("NEW MESSAGE IN ROOM '{}'".format(room.title))
    print("FROM '{}'".format(person.displayName))
    print("MESSAGE '{}'\n".format(message.text))

    if message.personId == me.id:
        return 'OK'
    else:
        if("find" in message.text):
            return_msg = getIP(message.text)
            if(return_msg != "not_valid"):
                DATA = {
                    'extra_vars': {
                        'host_ip_addr': return_msg,
                        'RoomId': room.id,
                        'bot_token': bot_token,
                        'apic': APIC_ADDR,
                        'apic_username': APIC_USER,
                        'apic_password': APIC_PASS
                    }
                }
                URL = 'http://' + str(awx_IP) + '/api/v2/job_templates/15/launch/'
                HEADERS = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + str(awx_token)}
                api.messages.create(room.id, text=str("Finding " + return_msg + " in fabric"))
                r = requests.post(URL, data = json.dumps(DATA), headers = HEADERS)
            else:
                pre, preTwo, ip = message.text.split(" ")
                api.messages.create(room.id, text=str("\'" + ip + "\'" + " is not a valid IPV4 address"))
        elif("Cohesity" in message.text):
            api.messages.create(room.id, text=str("Checking Cohesity now"))
            DATA = {
                    'extra_vars': {
                        'Return_Room': room.id,
                        'bot_token': bot_token
                    }
            }
            URL = 'http://' + str(awx_IP) + '/api/v2/job_templates/17/launch/'
            HEADERS = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + str(awx_token)}
            r = requests.post(URL, data = json.dumps(DATA), headers = HEADERS)
        elif("create contract" in message.text):
            api.messages.create(room.id, text=str("Creating contract now...."))
            message_arr = message.text.split(" ")
            DATA = {
                'extra_vars': {
                    "src_ip_addr":   message_arr[3],
                    "dst_ip_addr":   message_arr[4],
                    "subj_name":     message_arr[5],
                    "dst_port":      message_arr[6],
                    'apic':          APIC_ADDR,
                    'apic_username': APIC_USER,
                    'apic_password': APIC_PASS,
                    "bot_token":     bot_token,
                    "RoomId":       room.id
                }
            }
            URL = 'http://' + str(awx_IP) + '/api/v2/job_templates/18/launch/'
            HEADERS = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + str(awx_token)}
            r = requests.post(URL, data = json.dumps(DATA), headers = HEADERS)
        else:
            api.messages.create(room.id, text=str("Bot Help Page:  \n > @bot_name find IP_ADDRESS  \n Finds the IP Address within the ACI fabric, if not there will return not found. If its found will return information about it.  \n > @bot_name Cohesity  \n Checks Cohesity for jobs run and provides information about pass/fail as well as providing links to them  \n > @bot_name create contract SRC_IP DEST_IP SUBJ_NAME DST_PORT  \n Creats a contract in ACI with using the parameters provided"))
    return 'OK'
