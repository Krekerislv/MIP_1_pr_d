#================================
#   SET GLOBAL VARIABLES HERE   |
#================================

# Tree generation depth limit
LIMIT = 10

# Save tree in files as it generates
# 1 file for every LIMIT levels
SAVE_TREE = False

# How many moves player has when starting the game
INITIAL_MOVE_COUNT = 4

# How many moves player gets when the first set of moves run out
MOVE_COUNT = 4

# Generate random moves for FIRST (and only first) set
RANDOM_MOVES = False

#If set to True, CPU will be maximizer, otherwise CPU will be minimizer
CPU_IS_MAXIMIZER = True


#================================
#   SET HEURISTIC WEIGHTS HERE  |
#================================
WEIGHTS = {
    "distance":1,
    "available_moves":0.1,
    "ladder_distance":1,
    "snake_distance":-1,
    "blocked":-0.1
}

"""
Factors:
    1) distance to finish: the closer to finish, the beter (max value = 100)
    2) available moves: the more available moves in next state, the better (max value = 6)
    3) ladder distance: if player climbs up a ladder in next move, state is more valuable (highest ladder = 45 tiles)
    4) snake distance: if player slides down a snake in next move, state is less valuable (lowest slide = 43 tiles)
    5) blocked: if player's available moves drop by more than 1, it means that it has a blocked move (maximum blocked moves = 1)
    6) all moves blocked: if player has all moves blocked by opponent, it is guaranteed to lose. In this case score = -inf.
    ...
"""