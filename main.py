import os

import discord, json, player, random, asyncio
from dotenv import load_dotenv
from tinydb import TinyDB, Query
from types import SimpleNamespace
from discord.ext import commands
from pulp import *
import numpy as np
import math
from willump import Willump
from discord import ui, interactions, app_commands
import gameReader
import matchmaker

# TODO Elo Mapping
# TODO join/leave for matches
# TODO Match Logic
# TODO WebServices
# TODO integrate matchmaker
# TODO elo calculations


redTeam = []
blueTeam = []
redRating = 0
blueRating = 0
players = {}
activePlayers = {}
load_dotenv()
db = TinyDB('newDB.json')
query = Query()
playerTable = db.table('players')

for item in playerTable:
    _x = str(item).replace("\'", "\"")
    x = json.loads(_x, object_hook=lambda d: SimpleNamespace(**d))
    p = player.Player(x.name, x.discordHandle, x.ClientPUUID, x.RiotPUUID, x.elo, x.games, x.wins)
    players[x.discordHandle] = p

# Discord Stuff
# ----------------------------------------------------------------------------------------------#
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='&', intents=intents, help_command=None)


# ----------------------------------------------------------------------------------------------#

# Returns PUUID by Summoner Name
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


# Sync Slash-Commands
@bot.event
async def on_ready():
    await bot.tree.sync()  # Syncs all slash commands
    print(f"Logged in as {bot.user}")
    asyncio.create_task(gameReader.run_reader())

@bot.command()
async def help(ctx):

    pass

# Join the In-House Session
@bot.command()
async def join(ctx):
    p = playerTable.search(query.discordHandle == str(ctx.author))[0]
    if p is None:
        await ctx.send("You are not in the Database, run /add_user to register.")
        return
    else:
        activePlayers[p["discordHandle"]] = p
        await ctx.send("You successfully joined the session.")
    pass


# Leave the in-house session
@bot.command()
async def leave(ctx):
    if activePlayers.__contains__(str(ctx.author)):
        del activePlayers[str(ctx.author)]
        await ctx.send("You successfully left the session.")
    else:
        await ctx.send("You are not in the current session.")
    pass


# See stats for the specified player
@bot.command()
async def user(ctx, *args):
    members = ctx.message.mentions
    if len(args) == 0:  # Info about yourself
        p = playerTable.search(query.discordHandle == str(ctx.author))
        print(p)
        if len(p) > 0:  # player exists
            x = json.loads(str(p[0]).replace("\'", "\""), object_hook=lambda d: SimpleNamespace(**d))
            _p = player.Player(x.name, x.discordHandle, x.ClientPUUID, x.RiotPUUID, x.elo, x.games, x.wins)
            await ctx.reply(_p)
        else:
            await ctx.reply("Player not in database.")
    elif len(args) == 1:  # Info about someone else
        if len(members) != 1:
            await ctx.reply("Wrong format. Please specify one or no players.")
        else:
            p = playerTable.search(query.discordHandle == str(members[0]))
            if len(p) > 0:  # player exists
                x = json.loads(str(p[0]).replace("\'", "\""), object_hook=lambda d: SimpleNamespace(**d))
                _p = player.Player(x.name, x.discordHandle, x.ClientPUUID, x.RiotPUUID, x.elo, x.games, x.wins)
                await ctx.reply(_p)
            else:
                await ctx.reply("Player not in database.")
    else:
        await ctx.reply("Wrong format. Please specify one or no players.")


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


# TODO
@bot.command()
async def win(ctx, *args):

    pass


# TODO
# Start the in-house session
@bot.command()
async def start_session(ctx):
    if len(activePlayers) != 10:
        await ctx.send("Not enough players or too many players in current session. Run &join if you want to join the session.")
    else:
        data = matchmaker.calcTeams(activePlayers)
        winProb(data["red"]["red_average"], data["blue"]["blue_average"])
        print(data)
    pass


# TODO Replace with functionality of matchmaker.py
# Shuffle Teams
async def shuffle(ctx, players):
    pass

#list active players in session
@bot.command()
async def list_players(ctx):
    if len(activePlayers) == 0:
        await ctx.send("No players in current session.")
    else:
        s = "Current players:\n"
        for k, v in activePlayers.items():
            s += f"{v["name"]}\n"
        await ctx.send(s)
    pass

# TODO
@bot.command()
async def resetTeams(ctx):
    global redTeam, blueTeam, redRating, blueRating
    redTeam = []
    blueTeam = []
    redRating = 0
    blueRating = 0
    await ctx.reply("Teams reset.")


# TODO
def winProb(rating1, rating2):
    winprob = 1.0 / (1.0 + math.pow(10, (rating1 - rating2) / 400))
    return winprob


# TODO fix elo shit on creation to put -1 in non role fields
# TODO make elo change command
# TODO
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


# TODO
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


# TODO
@bot.command()
async def update_elo(ctx, *args):
    if len(args) != 2:
        await ctx.reply(
            "Wrong Format. Please specify the role you want to edit and the value it should take on. (i.e top 1200)")
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


# TODO
def calcElo(ctx, user, roles) -> list[int]:
    elo = np.empty(5)
    elo.fill(-1)

    if ('top' in roles):
        elo[0] = 1200
    if ('jng' in roles):
        elo[1] = 1200
    if ('mid' in roles):
        elo[2] = 1200
    if ('adc' in roles):
        elo[3] = 1200
    if ('sup' in roles):
        elo[4] = 1200
    # user.elo = elo
    return elo.tolist()


# TODO
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
