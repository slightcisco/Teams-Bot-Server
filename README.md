# Python_ACI_Bot_Teams

## How to start

* Clone this repo
* Ensure you have python installed, and a working web connection
* Create an account and install NGROK from https://ngrok.com/
* Edit bot_server.py and include APIC details on lines 72-75
* Run the startup script with `python start.py`
  - It should take you through installing Flask and webex teams sdk
  - Starting NGROK
  - Creating a developer.webex.com account and bot. See https://developer.webex.com/docs/bots for more details
  - Creating and maintaining webhook
  - Saving Access token
  - Starting the python bot server
 * Now add the bot to a room with the address in developer.cisco.com and call it using the following:
  - `@BOT_NAME IP IP_ADDRESS`
  - `@BOT_NAME Cohesity`

## Usage

    ![Bot Gif](https://github.com/slightcisco/Python_ACI_Bot_Teams/blob/master/Ansiblebotvid.gif)
