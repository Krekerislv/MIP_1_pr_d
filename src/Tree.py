from copy import deepcopy
from PARAMS import MOVE_COUNT, LIMIT, WEIGHTS


class Node:
    def __init__(self, P1moves, P1name, P1boardNr, P2moves, P2name, P2boardNr, movingPlayer, level=0, score=0, minimaxScore=None, isMax=None):
        self.P1moves = P1moves #player
        self.P1name = P1name
        self.P1boardNr = P1boardNr
        self.level = level
        self.P2moves = P2moves #cpu
        self.P2name = P2name
        self.P2boardNr = P2boardNr
        self.score = score
        self.minimaxScore = minimaxScore
        self.reason = None #a string that states the reason of win/loss
        self.isMax = isMax #maximizing level or minimizing level

        self.movingPlayer = movingPlayer #name of starting player
        self.isTerminal = False
        self.P1_win = False
        self.P2_win = False

        self.children = []
        self.checkNode()

    def checkNode(self):
        if len(self.P1moves) == 0:
            self.P1moves = [i for i in range(1, MOVE_COUNT+1)]
        if len(self.P2moves) == 0:
            self.P2moves = [i for i in range(1, MOVE_COUNT+1)]


        self.P1_win = True
        self.reason = f"{self.P2name} has no|possible|moves left"
        for move in self.P2moves:
            if move + self.P2boardNr != self.P1boardNr:
                self.P1_win = False
                self.reason = None
        
        self.P2_win = True
        self.reason = f"{self.P1name} has no|possible|moves left"
        for move in self.P1moves:
            if move + self.P1boardNr != self.P2boardNr:
                self.P2_win = False
                self.reason = None

        #check if players have possible moves left
        for move in self.P1moves:
            if self.P1boardNr + move <= 100 or self.P1boardNr == 100:
                break
            self.P2_win = True
            self.reason = f"{self.P1name} has no|possible move|left"

        for move in self.P2moves:
            if self.P2boardNr + move <= 100 or self.P2boardNr == 100:
                break
            self.P1_win = True
            self.reason = f"{self.P2name} has no|possible moves|left"
                

        if self.P1boardNr == 100:
            self.P1_win = True #has won
            self.reason = f"{self.P1name} reached|finish!"
        elif self.P2boardNr == 100:
            self.P2_win = True #has won
            self.reason = f"{self.P2name} reached|finish!"

        #if node is terminal, no further checking is necessary
        self.isTerminal = self.P1_win or self.P2_win

    def addChild(self, node):
        self.children.append(node)

    def generateNodeInfo(self):
        string = f"Level:{self.level}:Move:{self.movingPlayer}|"
        string += f"{self.P1name}:{self.P1boardNr}:{self.P1moves}|"
        string += f"{self.P2name}:{self.P2boardNr}:{self.P2moves}|"
        string += f"MiniMax:{self.minimaxScore}|Score:{self.score}|"

        if self.isMax:
            string += "MAX|"
        else:
            string += "MIN|"

        if self.isTerminal:
            string += "■"
        
        if self.P1_win:
            string += f"✔{self.P1name}"
        if self.P2_win:
            string += f"✔{self.P2name}"
        
        return string
    
    def heuristic(self, P1newMoves, P2newMoves, P1newBoardNr, P2newBoardNr, movingPlayerName, specialCases):
        #self represents the current state
        #movingPlayerName refers to the previous node (player whose move will lead to this (new) state)
        # higher score = better node (more likely to lead to terminal node (any of them))
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
        #=======DISTANCE TO FINISH========
        distance_p1 = P1newBoardNr / 100
        distance_p2 = P2newBoardNr / 100


        #=======AVAILABLE MOVE COUNT======
        available_moves_p1 = len(P1newMoves) / 6
        available_moves_p2 = len(P2newMoves) / 6

        #========LADDER AND SNAKE DISTANCE==========
            #specialCases contain all start and end points of snakes and ladders
            #keys - start points, values - end points
        ladder_distance_p1 = 0
        ladder_distance_p2 = 0
        snake_distance_p1 = 0
        snake_distance_p2 = 0
        for startPoint in specialCases.keys():
            endPoint = specialCases[startPoint]

            if endPoint == P1newBoardNr:
                # P1 has gone up a ladder or slid down a snake
                if endPoint > startPoint:
                    #climbed up a ladder
                    ladder_distance_p1 = (endPoint - startPoint) / 45
                else:
                    #slid down a snake
                    snake_distance_p1 = abs(endPoint - startPoint) / 43

            if endPoint == P2newBoardNr:
                 # P2 has gone up a ladder or slid down a snake
                if endPoint > startPoint:
                    #climbed up a ladder
                    ladder_distance_p2 = (endPoint - startPoint) / 45
                else:
                    #slid down a snake
                    snake_distance_p2 = abs(endPoint - startPoint) / 43


        #====BLOCKED AND ALL MOVES BLOCKED=================
        P1_all_moves_blocked = True #if P1 is behind P2 and all P1's moves lead to position of P2, this will remain true
        P2_all_moves_blocked = True #if P2 is behind P1 and all P2's moves lead to position of P1, this will remain true
        P1_is_blocked = 0
        P2_is_blocked = 0

        for moveP2 in P2newMoves:
            if P2newBoardNr + moveP2 != P1newBoardNr: 
                P2_all_moves_blocked = False
            else:
                P2_is_blocked = 1

        for moveP1 in P1newMoves:
            if P1newBoardNr + moveP1 != P2newBoardNr:
                P1_all_moves_blocked = False
            else:
                P1_is_blocked = 1

        #======CALCULATE SCORE FOR EACH PLAYER=============
        P1_score = WEIGHTS["distance"] * distance_p1 + WEIGHTS["available_moves"] * available_moves_p1 + WEIGHTS["ladder_distance"] * ladder_distance_p1 + WEIGHTS["snake_distance"] * snake_distance_p1 + WEIGHTS["blocked"] * P1_is_blocked
        P2_score = WEIGHTS["distance"] * distance_p2 + WEIGHTS["available_moves"] * available_moves_p2 + WEIGHTS["ladder_distance"] * ladder_distance_p2 + WEIGHTS["snake_distance"] * snake_distance_p2 + WEIGHTS["blocked"] * P2_is_blocked

        #======RETURN MOVING PLAYER'S SCORE================
        if movingPlayerName == self.P1name:
            if P1_all_moves_blocked:
                return float("-inf")
            else:
                return P1_score
        else:
            if P2_all_moves_blocked:
                return float("-inf")
            else:
                return P2_score
     
    def generateChildren(self, specialCases, level):
        """
            RULES:
                Each player has 6 available moves at the beggining: 1, 2, 3, 4, 5, 6.
                When a player moves, the move used is not available anymore.
                When player runs out of all moves, they are reset to 1, 2, 3, 4, 5, 6.
                Two players cannot be on the same tile. If opponent in front is close enough, the move
                that would lead to opponent's position is *removed* from moving players available moves.
                If opponent is at the end tile of a specialCase (snakes and ladders) and moving player
                moves to the beggining tile of the same snake or ladder, player will remain at the beggining
                and not go up/down to satisfy the "two players cannot occupy the same tile rule".
                After opponent moves, player still *cannot* use snake or ladder to go up/down. 

                If player has only 1 available move and oponnent is blocking the new tile, player loses.
                If player is near finish and doesn't have the necessary move to finish the game or to move to any other tile, player loses.

                If player lands on tile nr. 100, player wins.
        """

        if self.isTerminal:
            return
        
        
        if self.movingPlayer == self.P1name:
            idlePlayerName = self.P2name
            moves = self.P1moves
            boardNr = self.P1boardNr
            occupiedBoardNr = self.P2boardNr
            otherPlayerMoves = self.P2moves
        else:
            idlePlayerName = self.P1name                
            moves = self.P2moves
            boardNr = self.P2boardNr
            occupiedBoardNr = self.P1boardNr
            otherPlayerMoves = self.P1moves

        #check if opponent is on specialCase tile
        takenSpecialCase = None
        if occupiedBoardNr in list(specialCases.values()):
            takenSpecialCase = occupiedBoardNr
        
        for move in moves:
            newMoves = deepcopy(moves)
            newOtherPlayerMoves = deepcopy(otherPlayerMoves)
            #define new boardNr if target is clear
            newBoardNr = boardNr + move
             
            if newBoardNr <= 100:

                #check if other player is at possible target
                if newBoardNr == occupiedBoardNr:
                    continue
        
                #if opponent is on specialCase endpoint
                #check if it's disturbing player's move
                if takenSpecialCase:
                    if newBoardNr in list(specialCases.keys()):
                        if takenSpecialCase != specialCases[newBoardNr]:
                            newBoardNr = specialCases[newBoardNr]
                elif newBoardNr in list(specialCases):
                    newBoardNr = specialCases[newBoardNr]

                #remove move from next node's available moves after performing it
                newMoves.remove(move)

                #remove opponent's move, if moving player blocks a tile
                for otherPlayerMove in otherPlayerMoves:
                    if occupiedBoardNr + otherPlayerMove == newBoardNr:
                        newOtherPlayerMoves.remove(otherPlayerMove)

                #generate next node:
                if self.movingPlayer == self.P1name:
                    P1newMoves = newMoves
                    P2newMoves = newOtherPlayerMoves
                    P1newBoardNr = newBoardNr
                    P2newBoardNr = self.P2boardNr
                else:
                    P1newMoves = newOtherPlayerMoves
                    P2newMoves = newMoves
                    P1newBoardNr = self.P1boardNr
                    P2newBoardNr = newBoardNr
                #caculate heuristic value for children node
                childScore = self.heuristic(P1newMoves, P2newMoves, P1newBoardNr, P2newBoardNr, self.movingPlayer, specialCases)

                node = Node(P1newMoves, self.P1name, P1newBoardNr, P2newMoves,
                            self.P2name, P2newBoardNr, idlePlayerName, level, childScore, isMax=not self.isMax)
                self.addChild(node)            
    
    def generateTree(self, specialCases, limit):
        
        if self.level >= limit:
            return
        
        self.generateChildren(specialCases, self.level+1)
        
        for child in self.children:
            self.score = None
            #if level <= limit:
            child.generateTree(specialCases, limit)

    def saveSubTree(self, **kwargs):
        indentCount = 0
        file =None
        for key, val in kwargs.items():
            if key == "file":
                file = val
            if key == "indent":
                indentCount = val

        
        indent = "\t"*indentCount
        file.write(indent+self.generateNodeInfo()+"\n")

        for child in self.children:
            child.saveSubTree(file=file, indent=indentCount + 1)

class Tree:
    def __init__(self, specialCases, gameMatrix, root):
        self.specialCases = specialCases
        self.gameMatrix = gameMatrix
        self.root = root    
           
    def generateTree(self, node, limit=LIMIT):
        node.generateTree(self.specialCases, limit)
    
    def saveTree(self, node, fileName):
        f = open(fileName, "w", encoding="utf-8")
        node.saveSubTree(file=f)
        f.close()
    
    #based on psuedocode from https://www.baeldung.com/cs/minimax-algorithm
    def minimax(self, node, maximizing_player, level=LIMIT):
        if level == 0 or node.isTerminal:
            node.minimaxScore = node.score
            return node.score

        #maximizing player's turn (CPU)
        if maximizing_player:
            max_score = -float('inf')
            for child in node.children:
                score = self.minimax(child, False, level - 1)
                if score > max_score:
                    max_score = score
            node.minimaxScore = max_score
            return max_score
        #minimizing players turn (Player)
        else:
            min_score = float('inf')
            for child in node.children:
                score = self.minimax(child, True, level - 1)
                if score < min_score:
                    min_score = score
                node.minimaxScore = min_score
            return min_score
