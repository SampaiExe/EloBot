from tinydb import TinyDB, Query

db = TinyDB("db.json")
db.truncate()
Player = Query()
# players = [
#         {"name": "Cheez",   "discordHandle": "lcz",                 "elo": [0,0,0,0,0],   "games": 0,     "wins": 0,  "roles": ""}, 
#         {"name": "Tien",    "discordHandle": "Tien",                "elo": [0,0,0,0,0],   "games": 0,     "wins": 0,  "roles": ""}, 
#         {"name": "David",   "discordHandle": "caladriusdavid",      "elo": [0,0,0,0,0],   "games": 0,     "wins": 0,  "roles": ""}, 
#         {"name": "Aydan",   "discordHandle": "shadowscontempt",     "elo": [0,0,0,0,0],   "games": 0,     "wins": 0,  "roles": ""}, 
#         {"name": "Simon",   "discordHandle": "_yava",               "elo": [0,0,0,0,0],   "games": 0,     "wins": 0,  "roles": ""}, 
#         {"name": "Axile",   "discordHandle": "kokichat",            "elo": [0,0,0,0,0],   "games": 0,     "wins": 0,  "roles": ""},  
#         {"name": "Keis",    "discordHandle": "keisxdd",             "elo": [0,0,0,0,0],   "games": 0,     "wins": 0,  "roles": ""}, 
#         {"name": "Sam",     "discordHandle": "sampai.exe",          "elo": [0,0,0,0,0],   "games": 0,     "wins": 0,  "roles": ""}, 
#         {"name": "Kevin",   "discordHandle": "tothericefields",     "elo": [0,0,0,0,0],   "games": 0,     "wins": 0,  "roles": ""}, 
#         {"name": "Charlie", "discordHandle": "hiimcharlie.",        "elo": [0,0,0,0,0],   "games": 0,     "wins": 0,  "roles": ""}, 
#         {"name": "Sanni",   "discordHandle": "sanstone",            "elo": [0,0,0,0,0],   "games": 0,     "wins": 0,  "roles": ""}  
#     ]
# db.insert_multiple(players)  