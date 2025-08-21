from pulp import *
from tinydb import TinyDB, Query


db = TinyDB('newDB.json')
players = db.table('players')
data = players.all()


# ---- canonical roles and teams
roles = ["top","jng","mid","adc","sup"]
teams = ["blue","red"]

# ---- normalize into players list + Elo matrix E[name][role]
def normalize_players(raw):
    # map common typos to canonical roles
    role_alias = {"jgl": "jng", "jungle":"jng", "support":"sup"}
    def fix_role(r):
        r = r.lower()
        return role_alias.get(r, r)

    entries = raw
    # print(entries)
    # entries = raw["_default"]
    # print(entries)
    players = []
    E = {}   # E[name][role] -> float (or -1 for ineligible)

    for entry in entries:
        name = entry["name"]
        elo_vec = entry["elo"]
        if len(elo_vec) != 5:
            raise ValueError(f"Elo vector for {name} must have length 5 in ROLES order {roles}.")
        players.append(name)
        E[name] = {}

        for idx, role in enumerate(roles):
            val = float(elo_vec[idx]) if elo_vec[idx] is not None else -1.0
            # if negative -> ineligible
            E[name][role] = val

    # for key in sorted(entries, key=lambda x: int(x)):  # keep numeric order
    #     rec = entries[key]
    #     name = rec["name"]
    #     # incoming 'elo' is a length-5 array aligned with ROLES order
    #     elo_vec = rec["elo"]
    #     # make sure length is 5 (top,jng,mid,adc,sup)
    #     if len(elo_vec) != 5:
    #         raise ValueError(f"Elo vector for {name} must have length 5 in ROLES order {ROLES}.")
    #
    #     players.append(name)
    #     E[name] = {}
    #     for idx, role in enumerate(roles):
    #         val = float(elo_vec[idx]) if elo_vec[idx] is not None else -1.0
    #         # if negative -> ineligible
    #         E[name][role] = val

    return players, E

def calcTeams(activePlayers):
    _activePlayers = [v for k, v in activePlayers.items()]
    print(_activePlayers)
    players, E = normalize_players(_activePlayers)

    model = LpProblem("Minimise_Elo_Difference_Between_Teams", LpMinimize)

    y = LpVariable.dicts("y", ((p,t,r) for p in players for t in teams for r in roles), lowBound=0, upBound=1,cat=LpBinary)

    # This checks if y is 1 for player p (if player p has been assigned to team t and role r)
    for p in players:
        model += lpSum(y[(p,t,r)] for t in teams for r in roles) == 1

    # This checks if there are exactly 1 roles per each team
    for t in teams:
        for r in roles:
            model += lpSum(y[(p,t,r)] for p in players) == 1

    # This checks if there is ineligibility: forces y=0 (unassignes player) when E[p][r] = -1 (player p cant play role r)
    for p in players:
        for t in teams:
            for r in roles:
                if E[p][r] < 0:
                    model += y[(p,t,r)] == 0


    # This is basically the solver's objective. We want the elo difference between the teams to be the lowest it can be.

    red_elo_sum = lpSum(E[p][r] * y[(p,"red",r)] for p in players for r in roles)
    blue_elo_sum = lpSum(E[p][r] * y[(p,"blue",r)] for p in players for r in roles)

    red_avg = red_elo_sum / 5
    blue_avg = blue_elo_sum / 5


    d = LpVariable("d", lowBound=0)

    model += d
    model += red_avg - blue_avg <= d
    model += blue_avg - red_avg <= d


    # --- Solve
    solver = PULP_CBC_CMD(msg=True)              # msg=False to silence logs
    # solver = PULP_CBC_CMD(msg=True, timeLimit=10, gapRel=0.0, threads=0)  # optional controls
    model.solve(solver)

    print("Status:", LpStatus[model.status])

    # --- Extract assignments
    red, blue = [], []
    for p in players:
        for r in roles:
            for t in teams:
                var = y[(p,t,r)]
                if value(var) > 0.5:
                    (red if t=="red" else blue).append((p, r, E[p][r]))

    # --- Compute totals/averages/gap from the model (so no rounding mistakes)
    red_sum  = value(lpSum(E[p][r] * y[(p,"red",  r)] for p in players for r in roles))
    blue_sum = value(lpSum(E[p][r] * y[(p,"blue", r)] for p in players for r in roles))
    red_avg, blue_avg = red_sum/5, blue_sum/5
    gap = abs(red_avg - blue_avg)

    data = {
        "red":
            {
                "red_team": red,
                "red_average": red_avg
            },
        "blue":
            {
                "blue_team": blue,
                "blue_average": blue_avg
            }
    }
    print("b ruh")
    print(data["red"]["red_team"])

    print("\nRED:")
    for p,r,elo in red:  print(f"  {r:<3}  {p:<10}  {elo}")
    print("\nBLUE:")
    for p,r,elo in blue: print(f"  {r:<3}  {p:<10}  {elo}")

    print(f"\nRed avg:  {red_avg:.2f}")
    print(f"Blue avg: {blue_avg:.2f}")
    print(f"Gap:      {gap:.2f}")

    return data
