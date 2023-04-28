import telnetlib
import sys
import time

from utils import get_faceit_data, get_user_id32, get_csgo_hours, check_for_csgo, get_data_from_csgostats, get_friends_list
from converter import convert_from32_to64, convert_to_steam_id64

# These are the IP and port of the console
localhost = "127.0.0.1"
port = "2121"

# This is the path to the userdata folder
steam_path = r"C:\Steam"
userdata_path = steam_path + r"\userdata"
user_id32 = get_user_id32(userdata_path) # This is the user's steam id32
user_id64 = convert_from32_to64(user_id32) # This is the user's steam id64

# csgostats.gg ranks data is from 0 to 18, meaning that 0 is Unranked and 18 is The Global Elite
ranks = {0: "Unranked", 1: "Silver I", 2: "Silver II", 3: "Silver III", 4: "Silver IV", 5: "Silver Elite", 6: "Silver Elite Master",
         7: "Gold Nova I", 8: "Gold Nova II", 9: "Gold Nova III", 10: "Gold Nova Master", 11: "Master Guardian I",
         12: "Master Guardian II", 13: "Master Guardian Elite", 14: "Distinguished Master Guardian",
         15: "Legendary Eagle", 16: "Legendary Eagle Master", 17: "Supreme Master First Class", 18: "The Global Elite"}

def get_players_data(tn) -> list:
    # Prints "status" in the console and tries to read all the players data
    tn.write(b"status\n")
    
    read = tn.expect([b"#end"], timeout=1.5)[2].decode("utf-8")
    
    # Checks if the user is connected to a server
    if read.strip() == "Not connected to server":
        print("Join a server and then run the script again.")
        sys.exit(-1)

    tn.write(b"say_team Getting all players stats...\n")
    
    # Gets the players data from the console
    count = 0
    players_data = []
    for line in read.splitlines():
        if count > 8 and line != "#end":
            players_data.append(line)
        count += 1
    return players_data
    
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
    
    # Getting all players' data
    players_data = get_players_data(tn)
    users_friends = get_friends_list(user_id64)
    
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
        
        # This checks if the player is a friend of the user or if the player is the user
        STEAM_ID64 = convert_to_steam_id64(STEAM_ID)
        print(STEAM_ID64)
        if str(STEAM_ID64) in users_friends or STEAM_ID64 == user_id64: # Uncomment this if you want to see the data of all players including friends
            continue

        try:
            current_player_data = get_data_from_csgostats(STEAM_ID64)
            player_name = str(current_player_data['player_name'])
            player_rank = str(ranks[current_player_data['rank']])
        except:
            player_name = "N/A"
            player_rank = "N/A"
        
        try:
            faceit_data = get_faceit_data(STEAM_ID64)
            faceit_level = str(faceit_data['games']['csgo']['skill_level'])
        except:
            faceit_level = "N/A"
            
        try:
            hours = str(get_csgo_hours(STEAM_ID64))
        except:
            hours = "Private"
        
        # Prints the data to the console    
        message = str("Name: " + player_name + ' - ' + "Rank: " + player_rank + ' - Faceit level: ' + faceit_level + " - Hours: " + hours)
        
        tn.write(b"say_team " + message.encode("utf-8") + b"\n")
        time.sleep(0.15)
        
    tn.close()

if __name__ == "__main__":
    main()