from tinydb import TinyDB, Query

db = TinyDB("newDB.json")
db.truncate()
Player = Query()
playerTable = db.table("players")
playerTable.truncate()
players = [
        {"name": "Tien",        "discordHandle": "tienv",                "ClientPUUID": "6e61bdd4-fd08-588b-b34b-1cfc4b4a14b9", "RiotPUUID": "",    "elo": [775,-1,775,950,-1],          "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        {"name": "David",       "discordHandle": "caladriusdavid",      "ClientPUUID": "82f9c5a7-fb2d-5218-9afc-af7eaa79b667", "RiotPUUID": "",    "elo": [-1,850,-1,675,-1],           "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        {"name": "Sikos",       "discordHandle": "sikos",               "ClientPUUID": "51e0070b-7424-5b9b-ae9d-f2e57b4e6419", "RiotPUUID": "",    "elo": [820,-1,680,-1,700],          "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        {"name": "Omer",        "discordHandle": "xclsve.",             "ClientPUUID": "a0ba0b8f-e921-5dd3-9d92-d1f27cad40e3", "RiotPUUID": "",    "elo": [675,650,700,700,675],        "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        {"name": "Kevin",       "discordHandle": "tothericefields",     "ClientPUUID": "b002f5c2-a760-5d1c-b06b-d7bc6b9aad40", "RiotPUUID": "",    "elo": [676,550,-1,-1,-1],           "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        # {"name": "Sam",         "discordHandle": "sampai.exe",          "ClientPUUID": "e64d856e-64ba-527d-9cb0-7b456f9775e0", "RiotPUUID": "",    "elo": [450,-1,550,450,-1],          "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        {"name": "Lumi",        "discordHandle": "lumineszenz",         "ClientPUUID": "e225fdfe-ca49-58c2-9e5b-7a39637df5cb", "RiotPUUID": "",    "elo": [550,-1,600,650,650],         "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        {"name": "Keis",        "discordHandle": "keisxdd",             "ClientPUUID": "81a0dc8e-8d28-584e-b630-1f3064d052eb", "RiotPUUID": "",    "elo": [500,-1,500,650,600],         "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        {"name": "Simon",       "discordHandle": "yava",                "ClientPUUID": "8a12fae4-ed9f-51d4-b447-06418d881157", "RiotPUUID": "",    "elo": [550,600,730,650,800],        "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        {"name": "Cheez",       "discordHandle": "lcz",                 "ClientPUUID": "c83d819d-923b-565b-9ba8-5b210ab6bf37", "RiotPUUID": "",    "elo": [300,600,400,600,600],        "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        # {"name": "Aydan",     "discordHandle": "shadowscontempt",     "ClientPUUID": "dc1e4a13-3a8f-59ab-a3a0-53c64e434793", "RiotPUUID": "",    "elo": [0,0,0,0,0],                  "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        # {"name": "Fabian",    "discordHandle": "cupu5276",            "ClientPUUID": "20b51cdb-9d4a-5420-85d0-a411315b6b4b", "RiotPUUID": "",    "elo": [0,0,0,0,0],                  "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        # {"name": "Axile",     "discordHandle": "kokichat",            "ClientPUUID": "a72789ea-a1c1-5f7d-bcc0-fd009acafabf", "RiotPUUID": "",    "elo": [0,0,0,0,0],                  "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        # {"name": "Jack",      "discordHandle": "trouted",             "ClientPUUID": "dad17677-ca67-5dc1-b69d-66929bf92508", "RiotPUUID": "",    "elo": [0,0,0,0,0],                  "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        # {"name": "Furlash",   "discordHandle": "furlash",             "ClientPUUID": "10c9965b-4fab-597b-9cd1-dbdb5ec16ad1", "RiotPUUID": "",    "elo": [0,0,0,0,0],                  "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
        # {"name": "Ferum",     "discordHandle": "itsferum",            "ClientPUUID": "6353b641-9792-5ede-9e1a-ef67686aaccd", "RiotPUUID": "",    "elo": [0,0,0,0,0],                  "games": [0, 0, 0, 0, 0],     "wins": [0, 0, 0, 0, 0]},
    ]
playerTable.insert_multiple(players)