import os
import requests
from dotenv import load_dotenv
from tinydb import TinyDB, Query
import matchmaker
from main import activePlayers


db = TinyDB("newDB.json")
playerTable = db.table("players")
query = Query()
# load your Riot API key from .env
load_dotenv()
api_key = os.getenv("RIOT_API_KEY")

def get_puuid(game_name: str, tag_line: str, region="europe"):
    """Fetch the puuid for a player using IGN and tagline"""
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": api_key}
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        data = res.json()
        print(data)
        return data
    else:
        raise Exception(f"Error {res.status_code}: {res.text}")

# Example usage: user types their IGN + tagline
if __name__ == "__main__":
    print(data['red']["red_team"])
    ign = input("Enter IGN (game name): ")
    tag = input("Enter tagline (after #): ")
    puuid = get_puuid(ign, tag)
    print(f"PUUID for {ign}#{tag}: {puuid}")
