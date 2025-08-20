import persistent
from sympy.strategies.core import switch


class Player(persistent.Persistent):
    def __init__(self, name, discordHandle, ClientPUUID, RiotPUUID, elo=[0,0,0,0,0], games=[0,0,0,0,0], wins=[0,0,0,0,0]):
        self.name = name
        self.discordHandle = discordHandle
        self.ClientPUUID = ClientPUUID
        self.RiotPUUID = RiotPUUID
        self.elo = elo
        self.games = games
        self.wins = wins
        pass

    def getWinrate(self):
        winrates = []
        for g, w in zip(self.games, self.wins):
            if g > 0:
                winrates.append(w / g * 100)
            else:
                winrates.append(0.0)
        return winrates

    def getOverallWinrate(self):
        total_games = sum(self.games)
        total_wins = sum(self.wins)
        if total_games > 0:
            return total_wins / total_games * 100
        return 0.0
    

    
    # def win(self):
    #     games+=1
    #     wins+=1
    #     #TODO do something with elo
    #
    # def loss(self):
    #     games+=1
    #     #TODO do something with elo

    def elo_to_rank(self, elo) -> str:
        tiers = [
            ("Iron", 0, 99),
            ("Bronze", 100, 199),
            ("Silver", 200, 299),
            ("Gold", 300, 399),
            ("Plat", 400, 499),
            ("Emerald", 500, 599),
            ("Diamond", 600, 699),
        ]
        divisions = ["IV", "III", "II", "I"]

        # Handle Master / Grandmaster / Challenger separately
        if 700 <= elo <= 849:
            return "Master"
        elif 850 <= elo <= 999:
            return "Grandmaster"
        elif elo >= 1000:
            return "Challenger"

        # Find tier and division
        for tier, tier_min, tier_max in tiers:
            if tier_min <= elo <= tier_max:
                div_size = (tier_max - tier_min + 1) // 4
                div_index = (elo - tier_min) // div_size
                # Ensure division index is in range 0-3
                div_index = min(div_index, 3)
                return f"{tier} {divisions[div_index]}"

    def __str__(self):
        role_names = ["Top", "Jungle", "Mid", "ADC", "Support"]
        winrates = self.getWinrate()
        role_winrates = "\n".join(
            [f"{role}: {wr:.1f}%" for role, wr, e in zip(role_names, winrates, self.elo) if e != -1]
        )
        rank_strings = [self.elo_to_rank(e) for e in self.elo]

        elo_rank_strings = "\n".join(
            f"{role}: {e} ({r})"
            for role, e, r in zip(role_names, self.elo, rank_strings)
            if e != -1
        )
        overall_wr = self.getOverallWinrate()

        return (f"**Name:** {self.name}\n"
                f"**ELO per role:**\n{elo_rank_strings}\n"
                f"**Winrate per role:**\n{role_winrates}\n"
                f"**Overall Winrate:** {overall_wr:.1f}%")