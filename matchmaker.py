from pulp import *

# ---- canonical roles and teams
roles = ["top","jng","mid","adc","sup"]
teams = ["blue","red"]

# ---- your raw data (paste it into RAW_DATA)
RAW_DATA = {
  "_default": {
    "1": {"name":"Cheez","discordHandle":"lcz","elo":[-1,1730,1214,1400.0,1718],"games":10,"wins":6,"roles":["top","jng","mid","adc","sup"]},
    "2": {"name":"Aydan","discordHandle":"shadowscontempt","elo":[-1.0,-1.0,1653,1100,-1.0],"games":4,"wins":1,"roles":["mid","adc"]},
    "3": {"name":"Lumi","discordHandle":"lumineszenz","elo":[1197,-1,1201,1201,1201],"games":11,"wins":6,"roles":["top","jng","mid","adc"]},
    "4": {"name":"Sam","discordHandle":"sampai.exe","elo":[1000,-1,1030,-1,-1],"games":11,"wins":9,"roles":["top","mid","adc"]},
    "5": {"name":"Axile","discordHandle":"kokichat","elo":[1201,-1.0,1188,-1.0,-1.0],"games":11,"wins":3,"roles":["mid","top"]},
    "6": {"name":"Tien","discordHandle":"tienv","elo":[2000.0,-1,1999,2400.0,-1],"games":8,"wins":4,"roles":["top","mid","adc"]},
    "7": {"name":"Keis","discordHandle":"keisxdd","elo":[-1.0,-1.0,-1.0,1410,1484],"games":10,"wins":5,"roles":["sup","adc"]},
    "8": {"name":"Simon","discordHandle":"_yava","elo":[-1.0,-1.0,2013,-1.0,2028],"games":8,"wins":6,"roles":["sup","mid"]},
    "9": {"name":"David","discordHandle":"caladriusdavid","elo":[-1.0,2227,-1.0,2003,-1.0],"games":12,"wins":8,"roles":["adc","jgl"]},
    "10":{"name":"Sanni","discordHandle":"sanstone","elo":[1400,1200.0,1514,1700.0,1500],"games":1,"wins":1,"roles":["top","jng","mid","adc","sup"]}
  }
}

# ---- normalize into players list + Elo matrix E[name][role]
def normalize_players(raw):
    # map common typos to canonical roles
    role_alias = {"jgl": "jng", "jungle":"jng", "support":"sup"}
    def fix_role(r):
        r = r.lower()
        return role_alias.get(r, r)

    entries = raw["_default"]
    players = []
    E = {}   # E[name][role] -> float (or -1 for ineligible)

    for key in sorted(entries, key=lambda x: int(x)):  # keep numeric order
        rec = entries[key]
        name = rec["name"]
        # incoming 'elo' is a length-5 array aligned with ROLES order
        elo_vec = rec["elo"]
        # make sure length is 5 (top,jng,mid,adc,sup)
        if len(elo_vec) != 5:
            raise ValueError(f"Elo vector for {name} must have length 5 in ROLES order {ROLES}.")

        players.append(name)
        E[name] = {}
        for idx, role in enumerate(roles):
            val = float(elo_vec[idx]) if elo_vec[idx] is not None else -1.0
            # if negative -> ineligible
            E[name][role] = val

    return players, E

players, E = normalize_players(RAW_DATA)

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

print("\nRED:")
for p,r,elo in red:  print(f"  {r:<3}  {p:<10}  {elo}")
print("\nBLUE:")
for p,r,elo in blue: print(f"  {r:<3}  {p:<10}  {elo}")

print(f"\nRed avg:  {red_avg:.2f}")
print(f"Blue avg: {blue_avg:.2f}")
print(f"Gap:      {gap:.2f}")

