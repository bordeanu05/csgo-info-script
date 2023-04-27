import telnetlib
import psutil
import sys
import re
import time
import json
import requests
from bs4 import BeautifulSoup
import cloudscraper

# These are the IP and port of the console
localhost = "127.0.0.1"
port = "2121"

# csgostats.gg ranks data is from 0 to 18, meaning that 0 is Unranked and 18 is The Global Elite
ranks = {0: "Unranked", 1: "Silver I", 2: "Silver II", 3: "Silver III", 4: "Silver IV", 5: "Silver Elite", 6: "Silver Elite Master",
         7: "Gold Nova I", 8: "Gold Nova II", 9: "Gold Nova III", 10: "Gold Nova Master", 11: "Master Guardian I",
         12: "Master Guardian II", 13: "Master Guardian Elite", 14: "Distinguished Master Guardian",
         15: "Legendary Eagle", 16: "Legendary Eagle Master", 17: "Supreme Master First Class", 18: "The Global Elite"}

def check_for_csgo() -> bool:
    # Iterate over the all the running process
    for proc in psutil.process_iter(['name']):
        if proc.name().lower() == "csgo.exe":
            return True
    return False

def get_players_data(tn) -> list:
    # Prints "status" in the console and reads all the players data
    tn.write(b"status\n")
    read = tn.read_until(b"#end").decode("utf-8")
    
    # Checks if the user is connected to a server
    if read == "Not connected to server":
        print("Join a server and then run the script again.")
        sys.exit(-1)
    
    # Gets the players data from the console
    count = 0
    players_data = []
    for line in read.splitlines():
        if count > 8 and line != "#end":
            players_data.append(line)
        count += 1
    return players_data

# Converts the normal STEAM_ID to STEAM_ID64
def convert_to_steam_id64(steam_id) -> int:
    split = steam_id.split(":")
    return int(split[2]) * 2 + 76561197960265728 + int(split[1])

# Gets the data from csgostats.gg by scraping the website
def get_data_from_csgostats(STEAM_ID) -> dict:
    url = "https://csgostats.gg/player/"
    steam64 = convert_to_steam_id64(STEAM_ID)
    
    # Getting the HTML from the website
    flag = False
    while not flag:
        try:
            sc = cloudscraper.create_scraper()
            html_text = sc.get(url + str(steam64)).text
            flag = True
        except:
            continue
    
    # Getting the variable "stats" using regex
    p = re.compile('var stats = .*')
    soup = BeautifulSoup(html_text, 'lxml')
    scripts = soup.find_all('script')
    data = ''
    for script in scripts:
        try:
            m = p.match(script.string.strip())
            if m:
                data = m.group()
                break
        except:
            continue
        
    # Converting the variable "stats" to JSON    
    data_json = json.loads(data[12:-1])
    
    # This is in case the website doesn't have the data of the player
    if(type(data_json) == bool):
        return False
    
    # Getting the player name and adding it to the JSON
    name = soup.find('div', id='player-name').text.strip()
    data_json["player_name"] = name
    
    return data_json

# Gets the data from faceit.com by using their API
def get_faceit_data(STEAM_ID) -> dict:
    url = "https://open.faceit.com/data/v4/players"
    api_key = "API_KEY"
    headers = {
                'accept': 'application/json',
                'Authorization': 'Bearer {}'.format(api_key)
            }

    params = (
        ('game', 'csgo'),
        ('game_player_id', convert_to_steam_id64(STEAM_ID))
    )

    response = requests.get(url, headers=headers, params=params, timeout=5)
    response = response.json()
    
    return response

# Gets the data from the user's steam profile by using steam's web API
def get_csgo_hours(STEAM_ID) -> int:
    api_key = "API_KEY"
    steam64 = convert_to_steam_id64(STEAM_ID)
    steam_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam64}&format=json"
    
    response = requests.get(steam_url)
    response = response.json()
    
    # Checks if the user has CSGO
    for game in response['response']['games']:
        if game['appid'] == 730:
            return game['playtime_forever'] // 60 # Converts the playtime from minutes to hours
    
def main():
    # Checks if CSGO is running
    if not check_for_csgo():
        print("Open CSGO first.")
        sys.exit(1)
    
    # Tries to establish a connection with the console
    print("CSGO is running. Connecting to the console...")
    try:
        tn = telnetlib.Telnet(localhost, port)
    except:
        print("Could not connect to CSGO. This could be because you did not add -netconport 2121 to your launch options or because you have the Faceit Anticheat running.")
        sys.exit(-1)
    
    tn.write(b"say_team Getting all players stats...\n")
    players_data = get_players_data(tn)
    
    for player in players_data:
        splited_data = player.split()
        STEAM_ID = None
        for data in splited_data:
            if data.startswith("STEAM"):
                STEAM_ID = data
                break
        
        # This checks if the player is a bot
        if STEAM_ID is None:
            continue
        
        try:
            current_player_data = get_data_from_csgostats(STEAM_ID)
            player_name = str(current_player_data['player_name'])
            player_rank = str(ranks[current_player_data['rank']])
        except:
            player_name = "N/A"
            player_rank = "N/A"
        
        try:
            faceit_data = get_faceit_data(STEAM_ID)
            faceit_level = str(faceit_data['games']['csgo']['skill_level'])
        except:
            faceit_level = "N/A"
            
        try:
            hours = str(get_csgo_hours(STEAM_ID))
        except:
            hours = "Private"
        
        # Prints the data in the console    
        message = str("Name: " + player_name + ' - ' + "Rank: " + player_rank + ' - Faceit level: ' + faceit_level + " - Hours: " + hours)
        tn.write(b"say_team " + message.encode("utf-8") + b"\n")
        time.sleep(0.5)

if __name__ == "__main__":
    main()