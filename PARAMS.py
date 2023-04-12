#================================
#   SET GLOBAL VARIABLES HERE   |
#================================

# Tree generation depth limit
LIMIT = 11

# Save tree in files as it generates
# 1 file for every LIMIT levels
SAVE_TREE = False

# How many moves player has when starting the game
INITIAL_MOVE_COUNT = 3

# How many moves player gets when the first set of moves run out
MOVE_COUNT = 4

# Generate random moves for FIRST (and only first) set
RANDOM_MOVES = True

#if RANDOM_MOVES is set to False, starting player has a considerable advantage

#================================
#   SET HEURISTIC WEIGHTS HERE  |
#================================
WEIGHTS = {
    "distance":1,
    "available_moves":0.1
}

"""
Factors:
    1) distance to finish: the closer to finish, the beter (max value = 100)
    2) available moves: the more available moves in next state, the better
"""