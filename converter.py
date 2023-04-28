# Converts the normal STEAM_ID to STEAM_ID64
def convert_to_steam_id64(steam_id) -> int:
    split = steam_id.split(":")
    return int(split[2]) * 2 + 76561197960265728 + int(split[1])

# Converts STEAM_ID32 to STEAM_ID64
def convert_from32_to64(steam_id32) -> int:
    return int(steam_id32) + 76561197960265728