from copy import deepcopy

LIMIT = 5 #depth limit

class Node:
    def __init__(self, P1moves, P1name, P1boardNr, P2moves, P2name, P2boardNr, movingPlayer, level=0, score=0, minimaxScore=None):
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

        self.movingPlayer = movingPlayer #name of starting player
        self.isTerminal = False
        self.P1_win = False
        self.P2_win = False
        

        self.children = []
        self.checkNode()

    def checkNode(self):
        if len(self.P1moves) == 0:
            #print(f"setting default moves for P1 at level {self.level}")
            self.P1moves = [1,2,3,4,5,6]
        if len(self.P2moves) == 0:
            #print(f"setting default moves for P1 at level {self.level}")
            self.P2moves = [1,2,3,4,5,6]


        self.P1_win = True
        self.reason = f"{self.P2name} has no possible moves left"
        for move in self.P2moves:
            if move + self.P2boardNr != self.P1boardNr:
                self.P1_win = False
                self.reason = None
        
        self.P2_win = True
        self.reason = f"{self.P1name} has no possible moves left"
        for move in self.P1moves:
            if move + self.P1boardNr != self.P2boardNr:
                self.P2_win = False
                self.reason = None

        #check if players have possible moves left
        for move in self.P1moves:
            if self.P1boardNr + move <= 100 or self.P1boardNr == 100:
                break
            self.P2_win = True
            self.reason = f"{self.P1name} has no possible moves left"

        for move in self.P2moves:
            if self.P2boardNr + move <= 100 or self.P2boardNr == 100:
                break
            self.P1_win = True
            self.reason = f"{self.P2name} has no possible moves left"
                

        if self.P1boardNr == 100:
            self.P1_win = True #has won
            self.reason = f"{self.P1name} reached finish!"
        elif self.P2boardNr == 100:
            self.P2_win = True #has won
            self.reason = f"{self.P2name} reached finish!"

        #if node is terminal, no further checking is necessary
        self.isTerminal = self.P1_win or self.P2_win

    def addChild(self, node):
        self.children.append(node)

    def generateNodeInfo(self):
        string = f"Level:{self.level}:Move:{self.movingPlayer}:"
        string += f"{self.P1name}:{self.P1boardNr}:{self.P1moves}|"
        string += f"{self.P2name}:{self.P2boardNr}:{self.P2moves}|"
        string += f"MiniMax:{self.minimaxScore}|Score:{self.score}|"

        if self.movingPlayer == "Player":
            string += "MIN|"
        else:
            string += "MAX|"

        if self.isTerminal:
            string += "■"
        
        if self.P1_win:
            string += f"✔{self.P1name}"
        if self.P2_win:
            string += f"✔{self.P2name}"
        
        return string
    
    def heuristic(self, P1newMoves, P2newMoves, P1newBoardNr, P2newBoardNr, movingPlayerName, specialCases):
        #movingPlayerName refers to the previous node
        # higher score = better node (more likely to lead to terminal node (any of them))
        finish = 100
        max_moves = 6
        #set weights
        distance_weight = 2
        moves_weight = 2
        ladder_weight = 5
        ladder_distance_weight = 1.5
        snake_distance_weight = -1.5

        snake_distance_weight = 2
        snake_weight = -5
        blocking_weight = 1

        
        #lesser the distance, the better
        distance_p1 = P1newBoardNr
        distance_p2 = P2newBoardNr

        
        #more available moves -> better
        availableMovesBonus_p1 = len(P1newMoves) * moves_weight
        availableMovesBonus_p2 = len(P2newMoves) * moves_weight

        #calculate score from snakes and ladders ahead
        # if there are ladders in front of player, score is better
        # if ther are snakes in front of player, score is lower
        ladder_count_p1 = 0
        ladder_distance_p1 = 0
        snake_count_p1 = 0
        snake_distance_p1 = 0

        ladder_count_p2 = 0
        ladder_distance_p2 = 0
        snake_count_p2 = 0
        snake_distance_p2 = 0

        p1_blocked_weight = 5
        p2_blocked_weight = 5

        if P1newBoardNr >= 90:
            p1_blocked_weight = 10
        if P2newBoardNr >= 90:
            p2_blocked_weight = 10

        for case in specialCases.keys():
            #case - startPoint
            #specialCases[case] - endPoint of case
            if case > P1newBoardNr and specialCases[case] > P1newBoardNr:
                ladder_count_p1 += 1
                if specialCases[case] - case > ladder_distance_p1:
                    ladder_distance_p1 = specialCases[case] - case

            elif case > P1newBoardNr and specialCases[case] < P1newBoardNr:
                snake_count_p1 += 1
                if abs(specialCases[case] - case) > snake_distance_p1:
                    snake_distance_p1 = abs(specialCases[case] - case)



            if case > P2newBoardNr and specialCases[case] > P2newBoardNr:
                ladder_count_p2 += 1
                if specialCases[case] - case > ladder_distance_p2:
                    ladder_distance_p2 = specialCases[case] - case

            elif case > P2newBoardNr and specialCases[case] < P2newBoardNr:
                snake_count_p2 += 1
                if abs(specialCases[case] - case) > snake_distance_p2:
                    snake_distance_p2 = abs(specialCases[case] - case)


        #if opponent is being blocked
        P1_possibly_blocked_count = 0
        P2_possibly_blocked_count = 0
        P1_all_matching = True
        P2_all_matching = True
        for move in P2newMoves:
            next_p2_board_nr = P2newBoardNr + move
            for moveP1 in P1newMoves:
                next_p1_board_nr = P1newBoardNr + moveP1
                if next_p1_board_nr == next_p2_board_nr:
                    if P2newBoardNr > P1newBoardNr:
                        P1_possibly_blocked_count += 1
                    else:
                        P2_possibly_blocked_count += 1
                P1_all_matching = False
                P2_all_matching = False

       
        P1_score = distance_weight * distance_p1 + availableMovesBonus_p1 + ladder_distance_weight * ladder_distance_p1 + snake_distance_weight * snake_distance_p1 - p1_blocked_weight *  P1_possibly_blocked_count
        P2_score = distance_weight * distance_p2 + availableMovesBonus_p2 + ladder_distance_weight * ladder_distance_p2 + snake_distance_weight * snake_distance_p2 - p2_blocked_weight * P2_possibly_blocked_count

        if movingPlayerName == "Player":
            if P1_all_matching:
                return float("-inf")
            return P1_score
        else:
            if P2_all_matching:
                return float("-inf")
            return P2_score
     
    def generateChildren(self, specialCases, level):
        """
            RULES:
            1) each Node can have 1,2,3,4,5 or 6 children
            2) player cannot move to occupied tile
            3) if piece moves to beggining of specialCase path, but there's
                a piece at the enpoint, piece will remain at startpoint
        """

        if self.isTerminal:# and  (self.P1_win  or  self.P2_win):
            return
        
        
        if self.movingPlayer == self.P1name:
            idlePlayerName = self.P2name
            moves = self.P1moves
            boardNr = self.P1boardNr
            occupiedBoardNr = self.P2boardNr
        else:
            idlePlayerName = self.P1name                
            moves = self.P2moves
            boardNr = self.P2boardNr
            occupiedBoardNr = self.P1boardNr

        #check if opponent is on specialCase tile
        takenSpecialCase = None
        if occupiedBoardNr in list(specialCases.values()):
            takenSpecialCase = occupiedBoardNr
        
        for move in moves:
            newMoves = deepcopy(moves)
            if boardNr + move <= 100:

                #check if other player is at possible target
                if boardNr + move == occupiedBoardNr:
                    #print(f"removing {self.movingPlayer} move {move} from level {self.level}")
                    #moves.remove(move)
                    continue
        
                #define new boardNr if target is clear
                newBoardNr = boardNr + move
                
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

                #todo common move array?

                #generate next node:
                if self.movingPlayer == self.P1name:
                    P1newMoves = newMoves
                    P2newMoves = deepcopy(self.P2moves)
                    P1newBoardNr = newBoardNr
                    P2newBoardNr = self.P2boardNr
                else:
                    P1newMoves = deepcopy(self.P1moves)
                    P2newMoves = newMoves
                    P1newBoardNr = self.P1boardNr
                    P2newBoardNr = newBoardNr
                #caculate heuristic value for children node
                childScore = self.heuristic(P1newMoves, P2newMoves, P1newBoardNr, P2newBoardNr, self.movingPlayer, specialCases)

                node = Node(P1newMoves, self.P1name, P1newBoardNr, P2newMoves,
                            self.P2name, P2newBoardNr, idlePlayerName, level, childScore)
                #if node not in self.children:
                self.addChild(node)            
    
    def generateTree(self, specialCases, limit):
        
        if self.level >= limit:
            return
        
        self.generateChildren(specialCases, self.level+1)
        
        for child in self.children:
            self.score = None
            #if level <= limit:
            child.generateTree(specialCases, limit)

    def printTree(self, **kwargs):
        indentCount = 0
        file =None
        for key, val in kwargs.items():
            if key == "file":
                file = val
            if key == "indent":
                indentCount = val

        
        indent = "\t"*indentCount
        #print(f'writing: {indent+self.generateNodeInfo()}')
        file.write(indent+self.generateNodeInfo()+"\n")

        for child in self.children:
            child.printTree(file=file, indent=indentCount + 1)

class Tree:
    def __init__(self, specialCases, gameMatrix, root):
        self.specialCases = specialCases
        self.gameMatrix = gameMatrix
        self.root = root    
           
    def generateTree(self, node, limit=LIMIT):
        node.generateTree(self.specialCases, limit)
    
    def saveTree(self, node, fileName):
        f = open(fileName, "w", encoding="utf-8")
        node.printTree(file=f)
        f.close()
              
    def minimax(self, node, level=LIMIT, maximizing_player=True):
        if level == 0 or node.isTerminal:
            #print(f"minimax base score: {node.score}")
            node.minimaxScore = node.score
            #print(f"returning {node.score}")
            return node.score

        #maximizing player's turn (CPU)
        if maximizing_player:
            max_score = -float('inf')
            for child in node.children:
                score = self.minimax(child, level - 1, False)
                if score > max_score:
                    max_score = score
            #print(f"setting max score {max_score}")
            node.minimaxScore = max_score
            return max_score
        #minimizing players turn (Player)
        else:
            min_score = float('inf')
            for child in node.children:
                score = self.minimax(child, level - 1, True)
                if score < min_score:
                    min_score = score
                #print(f"setting min score {min_score}")
                node.minimaxScore = min_score
            return min_score
