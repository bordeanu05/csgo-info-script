# CSGO INFO SCRIPT
Python script that you can use to see players matchmaking ranks, Faceit levels and total hours played from your matches

# How to run it
First thing you have to do is to go to CSGO's launch options
and add ```-netconport 2121```

Run the following commands in the terminal:
``` bash
git clone https://github.com/bordeanu05/csgo-info-script.git
cd csgo-info-script
pip install -r requirements.txt
```
Go inside main.py in the ```get_faceit_data``` and ```get_csgo_hours``` functions and asign ```api_key = "API_KEY"``` to your own API keys

* Grab your Faceit API Key [here](https://developers.faceit.com/)
* Grab your Steam Web API Key [here](https://steamcommunity.com/dev/apikey)

Make sure you're connected to a CSGO server before running the script otherwise it won't work:
```
python main.py
```
Get back in the game and you will see the information getting typed in chat

The Faceit rank is requested from the Faceit developer API, while the matchmaking rank is obtained from [csgostats.gg](csgostats.gg) through web scraping using
[cloudscraper](https://pypi.org/project/cloudscraper/). The total hours played are also obtained from sending a get request to Steam's Web API.

- This script is totally safe and wil not cause any VAC or game bans as it does not interfere with the game process in any way.
- Having the Faceit Anticheat turned on will make it impossible for the script to connect to CSGO's console.

**Here is an example of what you should see after running the script and going back in the game:**

<img src="https://github.com/bordeanu05/csgo-info-script/blob/main/screenshot.png" />