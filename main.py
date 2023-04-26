import telnetlib
import psutil
import sys
import re
import time
import json
import requests
from bs4 import BeautifulSoup
import cloudscraper

localhost = "127.0.0.1"
port = "2121"

ranks = {0: "Unranked", 1: "Silver I", 2: "Silver II", 3: "Silver III", 4: "Silver IV", 5: "Silver Elite", 6: "Silver Elite Master",
          7: "Gold Nova I", 8: "Gold Nova II", 9: "Gold Nova III", 10: "Gold Nova Master", 11: "Master Guardian I",
           12: "Master Guardian II", 13: "Master Guardian Elite", 14: "Distinguished Master Guardian",
            15: "Legendary Eagle", 16: "Legendary Eagle Master", 17: "Supreme Master First Class", 18: "The Global Elite"}

def check_for_csgo():
    for proc in psutil.process_iter(['name']):
        if proc.name().lower() == "csgo.exe":
            return True
    return False

def get_players_data(tn):
    tn.write(b"status\n")
    read = tn.read_until(b"#end").decode("utf-8")
    count = 0
    players_data = []
    for line in read.splitlines():
        if count > 8 and line != "#end":
            players_data.append(line)
        count += 1
    return players_data


url = "https://csgostats.gg/player/"

def convert_to_steam_id64(steam_id):
    split = steam_id.split(":")
    return int(split[2]) * 2 + 76561197960265728 + int(split[1])
    
def get_data_from_csgostats(STEAM_ID):
    steam64 = convert_to_steam_id64(STEAM_ID)
    flag = False
    while not flag:
        try:
            sc = cloudscraper.create_scraper()
            html_text = sc.get(url + str(steam64)).text
            flag = True
        except:
            continue
    
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
        
    data_json = json.loads(data[12:-1])
    
    if(type(data_json) == bool):
        return False
    
    name = soup.find('div', id='player-name').text.strip()
    data_json["player_name"] = name
    
    return data_json
            
def get_faceit_data(STEAM_ID):
    api_key = "API_KEY"
    headers = {
                'accept': 'application/json',
                'Authorization': 'Bearer {}'.format(api_key)
            }

    params = (
        ('game', 'csgo'),
        ('game_player_id', convert_to_steam_id64(STEAM_ID))
    )

    response = requests.get('https://open.faceit.com/data/v4/players', headers=headers, params=params, timeout=5)
    response = response.json()
    
    return response
    
def main():
    if not check_for_csgo():
        print("Open CSGO first.")
        sys.exit(1)
    
    print("CSGO is running. Connecting to server...")
    try:
        tn = telnetlib.Telnet(localhost, port)
    except:
        print("Could not connect to CSGO. Make sure you put this as your launch option: -netconport 2121")
        sys.exit(-1)
    
    tn.write(b"say Getting all players stats...\n")
    players_data = get_players_data(tn)
    C = 0
    for player in players_data:
        splited_data = player.split()
        STEAM_ID = None
        for data in splited_data:
            if data.startswith("STEAM"):
                STEAM_ID = data
                break
        
        try:
            current_player_data = get_data_from_csgostats(STEAM_ID)
            player_name = "Name: " + str(current_player_data['player_name'])
            player_rank = "Rank: " + str(ranks[current_player_data['rank']])
        except:
            player_name = "Name: N/A"
            player_rank = "Rank: N/A"
        
        try:
            faceit_data = get_faceit_data(STEAM_ID)
            faceit_level = faceit_data['games']['csgo']['skill_level']
        except:
            faceit_level = "N/A"
            
        message = str(player_name + ' - ' + player_rank + ' - Faceit level: ' + str(faceit_level))
        tn.write(b"say_team " + message.encode("utf-8") + b"\n")
        time.sleep(0.5)

if __name__ == "__main__":
    main()