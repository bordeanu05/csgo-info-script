import requests
import os
import psutil
import cloudscraper
import json
import re
import api_keys
import sys

from bs4 import BeautifulSoup

# This is how I get the user's steam id
def get_user_id32(userdata_path) -> str:
    user_ids = os.listdir(userdata_path)
    return str(user_ids[0])

# Checks if CSGO is running
def check_for_csgo() -> bool:
    # Iterate over the all the running process
    for proc in psutil.process_iter(['name']):
        if proc.name().lower() == "csgo.exe":
            return True
    return False

# Gets the data from faceit.com by using their API
def get_faceit_data(STEAM_ID64) -> dict:
    url = "https://open.faceit.com/data/v4/players"
    api_key = api_keys.faceit_api_key
    
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer {}'.format(api_key)
    }

    params = (
        ('game', 'csgo'),
        ('game_player_id', STEAM_ID64)
    )

    response = requests.get(url, headers=headers, params=params, timeout=5)
    response = response.json()
    
    return response

# Gets the data from the user's steam profile by using steam's web API
def get_csgo_hours(STEAM_ID64) -> int:
    api_key = api_keys.steam_web_api_key
    steam_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={STEAM_ID64}&format=json"
    
    response = requests.get(steam_url)
    response = response.json()
    
    # Checks if the user has CSGO
    for game in response['response']['games']:
        if game['appid'] == 730:
            minutes = game['playtime_forever'] 
            if minutes == 0: # Checks if the user put his game hours on private
                return "Private"
            return minutes // 60 # Converts the playtime from minutes to hours

# Gets the user's friends list
def get_friends_list(STEAM_ID64) -> list:
    try:
        url = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={api_keys.steam_web_api_key}&steamid={STEAM_ID64}&relationship=friend"
        response = requests.get(url).json()
        friends_list = []
        for friend in response['friendslist']['friends']:
            friends_list.append(friend['steamid'])
    except:
        print("Error getting your friends list! Make sure your friends list is public!")
        sys.exit(1)
        
    return friends_list

# Gets the data from csgostats.gg by scraping the website
def get_data_from_csgostats(STEAM_ID64) -> dict:
    url = "https://csgostats.gg/player/"
    
    # Getting the HTML from the website
    flag = False
    while not flag:
        try:
            sc = cloudscraper.create_scraper()
            html_text = sc.get(url + str(STEAM_ID64)).text
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