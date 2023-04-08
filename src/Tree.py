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
        for move in self.P2moves:
            if move + self.P2boardNr != self.P1boardNr:
                self.P1_win = False
        
        self.P2_win = True
        for move in self.P1moves:
            if move + self.P1boardNr != self.P2boardNr:
                self.P2_win = False

        #check if players have possible moves left
        if self.P1boardNr == 100:
            self.P1_win = True #has won
        elif self.P2boardNr == 100:
            self.P2_win = True #has won

        #if node is terminal, no further checking is necessary
        self.isTerminal = self.P1_win or self.P2_win
        if self.isTerminal:
            return

        if self.P1name == self.movingPlayer:
            self.P2_win = True
            for move in self.P1moves:
                if self.P1boardNr + move <= 100:
                    self.P2_win = False
            

        elif self.P2name == self.movingPlayer:
            self.P1_win = True
            for move in self.P2moves:
                if self.P2boardNr + move <= 100:
                    self.P1_win = False      

    def addChild(self, node):
        self.children.append(node)

    def generateNodeInfo(self):
        string = f"Level:{self.level}:Move:{self.movingPlayer}:"
        string += f"{self.P1name}:{self.P1boardNr}:{self.P1moves}|"
        string += f"{self.P2name}:{self.P2boardNr}:{self.P2moves}|"
        string += f"MiniMax:{self.minimaxScore}|Score:{self.score}|"
    
        if self.isTerminal:
            string += "■"
        
        if self.P1_win:
            string += f"✔{self.P1name}"
        if self.P2_win:
            string += f"✔{self.P2name}"
        
        return string

    def heuristic(self, newMoves, newMaxBoardNr):
        #this is the heuristic function
        # higher score = better node
        # for start, program is going to prioritize highest boardNr
        # possible issue for this: might get fast to 90ish, but not have the right move
        # to finish the game
        return newMaxBoardNr 

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
                childScore = self.heuristic(newMoves, max(P1newBoardNr, P2newBoardNr))

                node = Node(P1newMoves, self.P1name, P1newBoardNr, P2newMoves,
                            self.P2name, P2newBoardNr, idlePlayerName, level, childScore)
                if node not in self.children:
                    self.addChild(node)            
    
    def generateTree(self, specialCases, limit):
        
        if self.level >= limit:
            return
        
        self.generateChildren(specialCases, self.level+1)

        for child in self.children:
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
            return node.score

        #maximizing player's turn
        if maximizing_player:
            max_score = -float('inf')
            for child in node.children:
                score = self.minimax(child, level - 1, False)
                max_score = max(max_score, score)
            #print(f"setting max score {max_score}")
            node.minimaxScore = max_score
            return max_score
        #minimizing players turn
        else:
            min_score = float('inf')
            for child in node.children:
                score = self.minimax(child, level - 1, True)
                min_score = min(min_score, score)
                #print(f"setting min score {min_score}")
                node.minimaxScore = min_score
            return min_score
