from pulp import *
import player, random
import numpy as np

np.set_printoptions(suppress=True)

roles = ['top', 'mid']
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

print(elo)