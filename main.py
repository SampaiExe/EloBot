import os

import discord, json, player, random
from dotenv import load_dotenv
from tinydb import TinyDB, Query
from types import SimpleNamespace
from discord.ext import commands
from pulp import *
import numpy as np
import math
from willump import Willump
from discord import ui, interactions, app_commands

#TODO Elo Mapping
#TODO join/leave for matches
#TODO Match Logic
#TODO WebServices
#TODO integrate matchmaker
#TODO elo calculations


redTeam = []
blueTeam = []
redRating = 0
blueRating = 0
players = {}
load_dotenv()
db = TinyDB('newDB.json')
query = Query()
playerTable = db.table('players')

for item in playerTable:
    _x = str(item).replace("\'", "\"")
    x = json.loads(_x, object_hook=lambda d: SimpleNamespace(**d))
    p = player.Player(x.name, x.discordHandle, x.ClientPUUID, x.RiotPUUID, x.elo, x.games, x.wins)
    players[x.discordHandle] = p

#Discord Stuff
#----------------------------------------------------------------------------------------------#
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='&', intents = intents, help_command=None)
#----------------------------------------------------------------------------------------------#
#Returns PUUID by Summoner Name
async def getUserPUUID(SummonerName):
    if SummonerName is None:
        return -1
    if not '#' in SummonerName:
        return -1

    tokens = SummonerName.split('#')

    wllp = await Willump().start()
    response = await wllp.request('get', f'/lol-summoner/v1/alias/lookup?gameName={tokens[0]}&tagLine={tokens[1]}')
    data = await response.json()
    return data['puuid']

@bot.command()
async def join(ctx):
    pass

@bot.command()
async def leave(ctx):
    pass

@bot.event
async def on_ready():
    await bot.tree.sync()  # Syncs all slash commands
    print(f"Logged in as {bot.user}")

# See stats for the specified player
@bot.command()
async def user(ctx, *args):
    members = ctx.message.mentions
    if len(args) == 0:  #Info about yourself
        p = playerTable.search(query.discordHandle == str(ctx.author))
        print(p)
        if len(p) > 0: #player exists
            x = json.loads(str(p[0]).replace("\'", "\""), object_hook=lambda d: SimpleNamespace(**d))
            _p = player.Player(x.name, x.discordHandle, x.ClientPUUID, x.RiotPUUID, x.elo, x.games, x.wins)
            await ctx.reply(_p)
        else:
            await ctx.reply("Player not in database.")
    elif len(args) == 1: #Info about someone else
        if len(members) != 1: 
            await ctx.reply("Wrong format. Please specify one or no players.")
        else:
            p = playerTable.search(query.discordHandle == str(members[0]))
            if len(p) > 0: #player exists
                x = json.loads(str(p[0]).replace("\'", "\""), object_hook=lambda d: SimpleNamespace(**d))
                _p = player.Player(x.name, x.discordHandle, x.ClientPUUID, x.RiotPUUID, x.elo, x.games, x.wins)
                await ctx.reply(_p)
            else:
                await ctx.reply("Player not in database.")
    else:
        await ctx.reply("Wrong format. Please specify one or no players.")

# #TODO
# @bot.command()
# async def add_user(ctx, *args):
#     mentions = ctx.message.mentions
#     print(mentions)
#     if len(mentions) != 1:
#         await ctx.reply("Wrong format. Name LeagueName#Tag.")
#     match len(args):
#         case 2:
#             #Username already in DB
#             if len(db.search(query.discordHandle == str(ctx.author))) != 0:
#                 await ctx.reply(f"Player {str(ctx.author)} already in database.")
#             else:
#                 puuid = getUserPUUID(args[1])
#                 db.insert({"name": args[0], "discordHandle": str(ctx.author), "ClientPUUID": puuid, "RiotPUUID": "",  "elo": elo, "games": [0,0,0,0,0], "wins": [0,0,0,0,0]})
#                 await ctx.reply(f'Successfully added {str(ctx.author)} to database as {args[0]}.')
#         case _:
#             await ctx.reply("Wrong format. Please @player and specify their name or specify your name if you want to add yourself as a player.")

class RegisterModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Register Player")
        # Basic info
        self.display_name_input = ui.TextInput(
            label="Display Name",
            placeholder="How you want to be called",
            custom_id="discord_name",
            style=discord.TextStyle.short,
        )
        self.league_name_input = ui.TextInput(
            label="League Name",
            placeholder="SummonerName#Tag",
            custom_id="league_name",
            style=discord.TextStyle.short,
        )

        self.elo_input = ui.TextInput(
            label="Elos per role",
            placeholder="TOP, JNG, MID, ADC, SUP | -1 if you do not play the role.",
            custom_id="elos_per_role",
            style=discord.TextStyle.short,
        )
        self.add_item(self.display_name_input)
        self.add_item(self.league_name_input)
        self.add_item(self.elo_input)

    async def on_submit(self, interaction: discord.Interaction):
        discord_name = self.display_name_input.value.strip()
        league_name = self.league_name_input.value.strip()

        # Parse ELOs
        try:
            elo_list = [int(e.strip()) for e in self.elo_input.value.split(",")]
            if len(elo_list) != 5:
                await interaction.response.send_message(
                    "Please provide exactly 5 ELO values separated by commas.",
                    ephemeral=True
                )
                return
        except ValueError:
            await interaction.response.send_message(
                "Invalid ELO values. Use integers separated by commas.",
                ephemeral=True
            )
            return

        # Check if user exists
        if playerTable.search(query.discordHandle == str(interaction.user)):
            await interaction.response.send_message(
                f"You are already registered in the database.",
                ephemeral=True
            )
            return

        # Get PUUID
        puuid = await getUserPUUID(league_name)  # your function to get Riot PUUID
        if puuid == -1:
            await interaction.response.send_message(
                f"Summoner not found",
                ephemeral=True
            )
            return
        # Insert into DB
        playerTable.insert({
            "name": discord_name,
            "discordHandle": str(interaction.user),
            "ClientPUUID": puuid,
            "RiotPUUID": "",
            "elo": elo_list,
            "games": [0, 0, 0, 0, 0],
            "wins": [0, 0, 0, 0, 0]


        })

        await interaction.response.send_message(
            f"Successfully registered {discord_name}!",
            ephemeral=True
        )


@bot.tree.command(name="add_user", description="Register yourself")
async def add_user(interaction: discord.Interaction):
    modal = RegisterModal()
    await interaction.response.send_modal(modal)


#TODO
@bot.command()
async def win(ctx, *args):
    global redTeam, blueTeam, redRating, blueRating
    if (len(redTeam) != 5 or len(blueTeam) != 5):
        await ctx.reply("There are no current teams.")
    elif (len(args) != 1):
        await ctx.reply("Format error. Please specify the winning team.")
    else:
        winner = args[0].lower()
        Pt1 = winProb(blueRating, redRating)
        Pt2 = winProb(redRating, blueRating)
        if (winner == "red" or winner == "team 1" or winner == "team1"):
            for player in redTeam:
                db.update({'games': player.games+1}, query.discordHandle == player.discordHandle)
                db.update({'wins': player.wins+1}, query.discordHandle == player.discordHandle)
                # Ra = Ra + K * (1-Pt1)
                # Rb = Rb + K * (0-Pt2)
                player.elo[player.rolePlayed] = round(player.elo[player.rolePlayed] + 30 * (1-Pt1))
                db.update({'elo': player.elo}, query.discordHandle == player.discordHandle)
            for player in blueTeam:
                db.update({'games': player.games+1}, query.discordHandle == player.discordHandle)
                player.elo[player.rolePlayed] = round(player.elo[player.rolePlayed] + 30 * (0-Pt2))
                db.update({'elo': player.elo}, query.discordHandle == player.discordHandle)
            redRating = 0
            blueRating = 0
            redTeam = []
            blueTeam = []
        elif (winner == "blue" or winner == "team 2" or winner == "team2"):
            for player in blueTeam:
                db.update({'games': player.games+1}, query.discordHandle == player.discordHandle)
                db.update({'wins': player.wins+1}, query.discordHandle == player.discordHandle)
                #Ra = Ra + K * (0-Pt1)
                #Rb = Rb + K * (1-Pt2)
                player.elo[player.rolePlayed] = round(player.elo[player.rolePlayed] + 30 * (1-Pt2))
                db.update({'elo': player.elo}, query.discordHandle == player.discordHandle)
            for player in redTeam:
                db.update({'games': player.games+1}, query.discordHandle == player.discordHandle)
                player.elo[player.rolePlayed] = round(player.elo[player.rolePlayed] + 30 * (0-Pt1))
                db.update({'elo': player.elo}, query.discordHandle == player.discordHandle)
            redRating = 0
            blueRating = 0
            redTeam = []
            blueTeam = []
        else:
            await ctx.reply("Unknown Team, please specify team1/team2 or red/blue")
    pass

#TODO
@bot.command()
async def start_session(ctx):
    global redTeam, blueTeam, redRating, blueRating

    if (len(redTeam) != 0 or len(blueTeam)!=0):
        await ctx.reply("Previous session still ongoing. Please declare a winner or reshuffle.")
        return
    guild = ctx.guild
    events = guild.scheduled_events
    activePlayer = []
    if events:
        print(events[0])
        if events[0].user_count < 0:
            await ctx.send("Not enough players to create teams. Blame Kevin.")
        else:
            s = "Current Players: \n"
            async for user in events[0].users():
                print(user)
                p = db.search(query.discordHandle == str(user))
                print(len(p))
                if len(p) > 0:
                    x = json.loads(str(p[0]).replace("\'", "\""), object_hook=lambda d: SimpleNamespace(**d))
                    _p = player.Player(x.name, x.discordHandle, x.ClientPUUID, x.RiotPUUID, x.elo, x.games, x.wins)
                    s += str(_p) + "\n"
                else:
                    userRoles = getUserRoles(ctx, user)
                    elo = calcElo(ctx, user, userRoles)
                    db.insert({"name": str(user), "discordHandle": str(user), "elo": elo, "games": 0, "wins": 0, "roles": userRoles})
                    p = str(db.search(query.discordHandle == str(user))[0]).replace("\'", "\"")
                    x = json.loads(p, object_hook=lambda d: SimpleNamespace(**d))
                    _p = player.Player(x.name, x.discordHandle, x.ClientPUUID, x.RiotPUUID, x.elo, x.games, x.wins)
                    s += str(_p) + "\n"
                activePlayer.append(_p)   
            await ctx.send(s)
            await shuffle(ctx, activePlayer)
    else:
        await ctx.reply("No scheduled events found.")

#TODO
async def shuffle(ctx, players):
    global redTeam, blueTeam, redRating, blueRating

    redTeam = []
    blueTeam = []
    prob = LpProblem("Minimize Elo Difference", LpMinimize)
    random.shuffle(players)
    # Extract Elo ratings of players
    elo_ratings = [player.elo for player in players]

    # Create binary variables for player assignment and Elo selection
    x = LpVariable.dicts("x", ((i, j) for i in range(10) for j in range(2)), cat='Binary')
    e = LpVariable.dicts("e", ((i, k) for i in range(10) for k in range(5)), cat='Binary')

    # Objective function: minimize the absolute difference between team average ratings
    diff = LpVariable("diff", lowBound=0)  # Absolute difference between team averages
    prob += diff

    # Auxiliary variables for product of Elo ratings and assignment variables
    prod = LpVariable.dicts("prod", ((i, j, k) for i in range(10) for j in range(2) for k in range(5)), cat='Continuous')

    # Additional binary variables to represent whether a player is assigned to a particular Elo bracket in each team
    y = LpVariable.dicts("y", ((i, j, k) for i in range(10) for j in range(2) for k in range(5)), cat='Binary')

    # Constraints
    for i in range(10):
        prob += lpSum(x[(i, j)] for j in range(2)) == 1  # Each player assigned to exactly one team
        prob += lpSum(e[(i, k)] for k in range(5)) == 1  # Each player has one chosen Elo
        for j in range(2):
            for k in range(5):
                prob += prod[(i, j, k)] == x[(i, j)] * elo_ratings[i][k]  # Define product variables
                prob += y[(i, j, k)] >= e[(i, k)] - x[(i, j)]
                prob += y[(i, j, k)] >= 0
                prob += y[(i, j, k)] <= 1

    # Add constraints to ensure only one player for each Elo bracket in each team
    for j in range(2):
        for k in range(5):
            prob += lpSum(y[(i, j, k)] for i in range(10)) <= 1

    # Constraints to ensure each team has exactly 5 players
    for j in range(2):
        prob += lpSum(x[(i, j)] for i in range(10)) == 5

    # Add constraint to prevent selection of Elo values equal to -1
    for i in range(10):
        for k in range(5):
            if elo_ratings[i][k] == -1:
                prob += e[(i, k)] == 0

    # Define the average ratings for each team
    avg_rating_team = [lpSum(prod[(i, j, k)] for i in range(10) for k in range(5)) / 5 for j in range(2)]

    # Define absolute difference between team averages
    prob += avg_rating_team[0] - avg_rating_team[1] <= diff
    prob += avg_rating_team[1] - avg_rating_team[0] <= diff

    # Solve the problem
    prob.solve()

    redRating = value(avg_rating_team[0])
    blueRating = value(avg_rating_team[1])
    print(redRating)
    print(blueRating)
    # Print results
    s = (f"Minimal average Elo difference: {value(prob.objective)} \n")
    s += ("Team 1 🔵: \n")
    for i in range(10):
        if value(x[(i, 0)]) == 1:
            chosen_elo_index = [k for k in range(5) if value(e[(i, k)]) == 1][0]
            match chosen_elo_index:
                case 0: role = "top"
                case 1: role = "jng"
                case 2: role = "mid"
                case 3: role = "adc"
                case 4: role = "sup"
            players[i].rolePlayed = chosen_elo_index
            s += (f"{players[i].name} | Role: {role} | Elo in Role: {elo_ratings[i][chosen_elo_index]} \n")
            redTeam.append(players[i])
    s+=("Team 2 🔴: \n")
    for i in range(10):
        if value(x[(i, 1)]) == 1:
            chosen_elo_index = [k for k in range(5) if value(e[(i, k)]) == 1][0]
            match chosen_elo_index:
                case 0: role = "top"
                case 1: role = "jng"
                case 2: role = "mid"
                case 3: role = "adc"
                case 4: role = "sup"
            players[i].rolePlayed = chosen_elo_index
            s+=(f"{players[i].name} | Role: {role} | Elo in Role: {elo_ratings[i][chosen_elo_index]} \n")
            blueTeam.append(players[i])
    await ctx.send(s)

#TODO
# Bot command to fetch scheduled events
@bot.command()
async def get_events(ctx):
    guild = ctx.guild
    events = guild.scheduled_events
    if events:
        await ctx.reply("Scheduled events:")
        for event in events:
            await ctx.send(event.name)
    else:
        await ctx.reply("No scheduled events found.")
#TODO
@bot.command() 
async def resetTeams(ctx):
    global redTeam, blueTeam, redRating, blueRating
    redTeam = []
    blueTeam = []
    redRating = 0
    blueRating = 0
    await ctx.reply("Teams reset.")
#TODO
@bot.command()
async def help(ctx):
    await ctx.send("***user @discordHandle***: Prints statistics for the specified user, if none were specified the author is considered the user. \n" +
                   "***add_user @discordHandle name***: Adds @discordHandle with the specified name to the database, if none were specified the author is considered the user. \n" +
                   "***start_session***: Starts the in-house session with all signed up users. If a user is not in the database they will be added automatically. This is also called to reshuffle teams. \n" +
                   "***win team***: Specifies the winning team. (i.e win team1) \n" +
                   "***add_role role***: Adds the specified role to the calling user. \n" +
                   "***remove_role role***: Removes the specified role to the calling user. \n" +
                   "***update_elo role elo***: Updates the elo for the specified role to the given value. \n"
                   )
#TODO
def getUserRoles(ctx, player) -> list[str]:
    userRoles = []
    guild = ctx.guild
    roles = guild.roles
    for role in roles:
        if role.name == "inhouse-fill":
            if(player in role.members):
                userRoles = ['top', 'jng', 'mid', 'adc', 'sup']
        elif role.name.startswith("inhouse-"):           
            if(player in role.members):
                userRoles.append(role.name.replace("inhouse-", ""))
    return userRoles
#TODO
def winProb(rating1, rating2):
    winprob = 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))
    return winprob

#TODO fix elo shit on creation to put -1 in non role fields
#TODO make elo change command
#TODO
@bot.command()
async def add_role(ctx, *args):
    if len(args) != 1:
        await ctx.reply("Wrong Format. Please specify the role you want to add. (i.e top)")
        return
    p = db.search(query.discordHandle == str(ctx.author))
    if len(p) < 1:
        await ctx.reply("Player not in database.")
        return
    x = json.loads(str(p[0]).replace("\'", "\""), object_hook=lambda d: SimpleNamespace(**d))
    _p = player.Player(x.name, x.discordHandle, x.ClientPUUID, x.RiotPUUID, x.elo, x.games, x.wins)

    if args[0] in _p.roles:
        await ctx.reply("User already has role: ", args[0])
    else:
        _p.roles.append(args[0])
        i = getRoleIndex(args[0])
        if i != -1:
            _p.elo[i] = 1200
            db.update({'roles': _p.roles}, query.discordHandle == str(ctx.author))
            db.update({'elo': _p.elo}, query.discordHandle == str(ctx.author))
            await ctx.reply("Roles successfully updated.")
        else:
            await ctx.reply("Unknown Role.")
#TODO
@bot.command()
async def remove_role(ctx, *args):
    if len(args) != 1:
        await ctx.reply("Wrong Format. Please specify the role you want to remove. (i.e top)")
        return
    p = db.search(query.discordHandle == str(ctx.author))
    if len(p) < 1:
        await ctx.reply("Player not in database.")
        return
    x = json.loads(str(p[0]).replace("\'", "\""), object_hook=lambda d: SimpleNamespace(**d))
    _p = player.Player(x.name, x.discordHandle, x.ClientPUUID, x.RiotPUUID, x.elo, x.games, x.wins)

    if args[0] not in _p.roles:
        await ctx.reply("User does not have role: ", args[0])
    else:
        _p.roles.remove(args[0])
        i = getRoleIndex(args[0])
        if i != -1:
            _p.elo[i] = -1
            db.update({'roles': _p.roles}, query.discordHandle == str(ctx.author))
            db.update({'elo': _p.elo}, query.discordHandle == str(ctx.author))
            await ctx.reply("Roles successfully updated.")
        else:
            await ctx.reply("Unknown Role.")
#TODO
@bot.command()
async def update_elo(ctx, *args):
    if len(args) != 2:
        await ctx.reply("Wrong Format. Please specify the role you want to edit and the value it should take on. (i.e top 1200)")
        return
    p = db.search(query.discordHandle == str(ctx.author))
    if len(p) < 1:
        await ctx.reply("Player not in database.")
        return
    x = json.loads(str(p[0]).replace("\'", "\""), object_hook=lambda d: SimpleNamespace(**d))
    _p = player.Player(x.name, x.discordHandle, x.ClientPUUID, x.RiotPUUID, x.elo, x.games, x.wins)

    if args[0] not in _p.roles:
        await ctx.reply("User does not have role: ", args[0])
    else:
        i = getRoleIndex(args[0])
        if i != -1:
            _p.elo[i] = int(args[1])
            db.update({'elo': _p.elo}, query.discordHandle == str(ctx.author))
            await ctx.reply("Elo successfully updated.")
        else:
            await ctx.reply("Unknown Role.")
    pass

#TODO
def calcElo(ctx, user, roles) -> list[int]:
    elo = np.empty(5)
    elo.fill(-1)

    if('top' in roles):
        elo[0] = 1200
    if('jng' in roles):
        elo[1] = 1200
    if('mid' in roles):
        elo[2] = 1200
    if('adc' in roles):
        elo[3] = 1200
    if('sup' in roles):
        elo[4] = 1200
    # user.elo = elo
    return elo.tolist()
#TODO
def getRoleIndex(role):
    match role:
        case 'top':
            return 0
        case 'jng':
            return 1
        case 'mid':
            return 2
        case 'adc':
            return 3
        case 'sup':
            return 4
        case _:
            return -1
bot.run(TOKEN)




