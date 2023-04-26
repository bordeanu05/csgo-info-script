# CSGO INFO SCRIPT
Simple script that you can use to see players matchmaking ranks and Faceit levels from your matches

# How to run it
Before installing anything you need to go to CSGO's launch options
and add ```-netconport 2121```

Run the following commands in the terminal
``` bash
git clone https://github.com/bordeanu05/csgo-info-script.git
cd csgo-info-script
pip install -r requirements.txt
```
Go inside main.py in the get_faceit_data function and asign ```api_key = "API_KEY"``` to your own API key

Make sure you're connected to a CSGO server before running the next command 
```
python main.py
```
Get back in the game and you will see the information getting typed in chat

The Faceit rank is requested from the Faceit developer API, while the matchmaking rank is obtained from [csgostats.gg](csgostats.gg) through web scraping using
[cloudscraper](https://pypi.org/project/cloudscraper/)

This script is totally safe and wil not cause any VAC or game bans as it does not interfere with the game process in any way.
