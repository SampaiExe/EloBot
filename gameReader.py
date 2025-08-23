import asyncio
import json
import signal
import contextlib
from types import SimpleNamespace

import requests
from sympy.strategies.core import switch
from willump import Willump
from tinydb import TinyDB, Query
import player

db = TinyDB('newDB.json')
query = Query()
playerTable = db.table('players')

# -------------------- Champion Mapping --------------------
def get_champion_map(version="15.16.1"):
    """Fetch championId -> championName mapping from DDragon"""
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    data = requests.get(url).json()
    return {int(c["key"]): c["id"] for c in data["data"].values()}


def updatePlayersInDB(players):
    for player in players:
        p = playerTable.search(query.ClientPUUID == player["puuid"])
        x = json.loads(str(p[0]).replace("\'", "\""), object_hook=lambda d: SimpleNamespace(**d))
        _p = player.Player(x.name, x.discordHandle, x.ClientPUUID, x.RiotPUUID, x.elo, x.games, x.wins)

        roleID = getRoleID(player["lane"], player["role"])
        if roleID == -1:
            return
        _p.games[roleID] += 1
        if player["win"]:
            _p.wins[roleID] += 1
            _p.elo[roleID] += calcElo


# -------------------- Match Parser --------------------
def parse_match(match_json, champion_map):
    """Returns list of players with identity + stats info"""
    identity_map = {i["participantId"]: i["player"] for i in match_json.get("participantIdentities", [])}
    players = []
    for p in match_json.get("participants", []):
        pid = p["participantId"]
        identity = identity_map.get(pid, {})
        stats = p.get("stats", {})
        timeline = p.get("timeline", {})

        champion_id = p.get("championId")
        champion_name = champion_map.get(champion_id, f"Unknown({champion_id})")

        total_cs = stats.get("totalMinionsKilled", 0) + stats.get("neutralMinionsKilled", 0)

        players.append({
            "summonerName": identity.get("summonerName") or identity.get("gameName", ""),
            "tagLine": identity.get("tagLine", ""),
            "champion": champion_name,
            "puuid": identity.get("puuid", ""),
            "lane": timeline.get("lane", "UNKNOWN"),
            "role": timeline.get("role", "UNKNOWN"),
            "roleID": 0,
            "teamId": p.get("teamId"),
            "kills": stats.get("kills", 0),
            "deaths": stats.get("deaths", 0),
            "assists": stats.get("assists", 0),
            "damageToChampions": stats.get("totalDamageDealtToChampions", 0),
            "totalCS": total_cs,
            "win": stats.get("win", False),
        })
    return players


def getRoleID(lane, role):
    match lane:
        case "TOP":
            return 0
        case "JUNGLE":
            return 1
        case "MIDDLE":
            return 2
        case "BOTTOM":
            if role == "CARRY": return 3
            else: return 4
        case _:
            return -1


# -------------------- Event Consumer --------------------
async def run_reader():
    wllp = await Willump().start()
    stop = asyncio.Event()

    # subscribe to all events
    subscription = await wllp.subscribe("OnJsonApiEvent")

    async def handle_eog(event):
        eog = event.get("data", {})
        game_id = eog.get("gameId")
        if not game_id:
            return
        print(f"[EOG] Game ended! gameId={game_id}")

        # fetch full match data from LCU
        response = await wllp.request("get", f"/lol-match-history/v1/games/{game_id}")
        game = await response.json()
        print(game)
        # derive version from match if possible
        game_version = "15.16.1"

        champion_map = get_champion_map(version=game_version)
        players = parse_match(game, champion_map)

        if eog.get("gameType") != "CUSTOM_GAME":
            print("Skipping non-custom game.")
            return -1

        if len(players) < 10:
            print("Skipping game, not enough players")
            return -1


        print(f"Parsed {len(players)} players from match {game_id}:")
        for p in players:
            tag = f"#{p['tagLine']}" if p["tagLine"] else ""
            print(f"  {p['summonerName']}{tag} - {p['champion']} ({p['role']}) | "
                  f"KDA {p['kills']}/{p['deaths']}/{p['assists']} | "
                  f"DMG {p['damageToChampions']} | CS {p['totalCS']} | "
                  f"{'Win' if p['win'] else 'Loss'}")

        return players


    # filter for end-of-game stats block
    wllp.subscription_filter_endpoint(subscription, "/lol-end-of-game/v1/eog-stats-block", handler=handle_eog)

    # graceful shutdown handling
    loop = asyncio.get_running_loop()
    try:
        loop.add_signal_handler(signal.SIGINT, stop.set)
        loop.add_signal_handler(signal.SIGTERM, stop.set)
    except NotImplementedError:
        pass

    try:
        await stop.wait()
    finally:
        with contextlib.suppress(Exception):
            await wllp.close()
        print("Shutdown cleanly.")

if __name__ == "__main__":
    try:
        asyncio.run(run_reader())
    except KeyboardInterrupt:
        # fallback if signal handling didn't trigger
        print("Interrupted by user")