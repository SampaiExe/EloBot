import persistent

class Player(persistent.Persistent):
    def __init__(self, name, discordHandle, elo=[0,0,0,0,0], games=0, wins=0, roles=[], rolePlayed=-1):
        self.name = name
        self.discordHandle = discordHandle
        self.elo = elo
        self.games = games
        self.wins = wins
        self.roles = roles
        self.rolePlayed = rolePlayed
        pass

    def getWinrate(self):
        return self.games/self.wins
    
    def __str__(self) -> str:
        printelo = []
        for i in self.elo:
            if i > -1:
                printelo.append(i)
        return f"{self.name} | {self.wins}W/{self.games-self.wins}L | current elo: {printelo} | roles: {self.roles}"
    
    def win(self):
        games+=1
        wins+=1
        #TODO do something with elo

    def loss(self):
        games+=1
        #TODO do something with elo
    
    