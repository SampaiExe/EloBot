import os

from dotenv import load_dotenv
import requests
import asyncio
import json
from willump import Willump

import requests

import requests


def get_champion_map(version="15.16.1"):
    """Fetch DDragon champion data and return championId -> championName"""
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    res = requests.get(url).json()
    return {int(c["key"]): c["id"] for c in res["data"].values()}


def get_champion_map(version="15.16.704.6097"):
    """Fetch championId -> championName mapping from DDragon"""
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    data = requests.get(url).json()
    return {int(c["key"]): c["id"] for c in data["data"].values()}


def parse_match(match_json, champion_map):
    """
    Returns a list of players with combined identity + stats info.
    """
    # Map participantId -> player identity
    identity_map = {i["participantId"]: i["player"] for i in match_json.get("participantIdentities", [])}

    players = []
    for p in match_json.get("participants", []):
        pid = p["participantId"]
        identity = identity_map.get(pid, {})
        stats = p.get("stats", {})
        timeline = p.get("timeline", {})

        champion_id = p.get("championId")
        champion_name = champion_map.get(champion_id, f"Unknown({champion_id})")

        # Compute total CS: fallback to totalMinionsKilled if timeline is empty
        total_cs = stats.get("totalMinionsKilled", 0) + stats.get("neutralMinionsKilled", 0)

        player_data = {
            "summonerName": identity.get("summonerName") or identity.get("gameName"),
            "tagLine": identity.get("tagLine", ""),
            "champion": champion_name,
            "role": timeline.get("lane", "UNKNOWN"),
            "teamId": p.get("teamId"),
            "kills": stats.get("kills", 0),
            "deaths": stats.get("deaths", 0),
            "assists": stats.get("assists", 0),
            "damageToChampions": stats.get("totalDamageDealtToChampions", 0),
            "totalCS": total_cs,
            "win": stats.get("win", False),
            "puuid": identity.get("puuid")
        }
        players.append(player_data)

    return players


async def main():
    wllp = await Willump().start()

    gameID = 7497261946
    response = await wllp.request('get', f'/lol-match-history/v1/games/{gameID}')
    game = await response.json()
    await wllp.close()

    champion_map = get_champion_map(version="15.16.1")  # use your match's gameVersion


    players = parse_match(game, champion_map)

    for p in players:
        print(f"{p['summonerName']}#{p['tagLine']} - {p['champion']} ({p['role']}) "
              f"KDA: {p['kills']}/{p['deaths']}/{p['assists']} DMG: {p['damageToChampions']} CS: {p['totalCS']} Win: {p['win']} : {p['puuid']}")

asyncio.run(main())


