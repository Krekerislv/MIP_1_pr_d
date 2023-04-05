from copy import deepcopy

LIMIT = 5 #depth limit

class Node:
    def __init__(self, P1moves, P1name, P1boardNr, P2moves, P2name, P2boardNr, startPlayer, level, score):
        self.P1moves = P1moves
        self.P1name = P1name
        self.P1boardNr = P1boardNr
        self.level = level
        self.P2moves = P2moves
        self.P2name = P2name
        self.P2boardNr = P2boardNr
        self.score = score

        self.movingPlayer = startPlayer #name of starting player

        self.P1_lose = False
        self.P2_lose = False
        self.isTerminal = False
        self.P1_win = False
        self.P2_win = False
        

        self.children = []
        self.checkNode()

    def checkNode(self):
        if self.P1boardNr == 100:
            self.P1_win = True #has won
        elif self.P2boardNr == 100:
            self.P2_win = True #has won

        if len(self.P1moves) == 0:
            self.P1moves = [1,2,3,4,5,6]
        if len(self.P2moves) == 0:
            self.P2moves = [1,2,3,4,5,6]

        if self.P1name == self.movingPlayer:
            self.P1_lose = True
            for move in self.P1moves:
                if self.P1boardNr + move <= 100:
                    self.P1_lose = False #still can win
            

        elif self.P2name == self.movingPlayer:
            self.P2_lose = True
            for move in self.P2moves:
                if self.P2boardNr + move <= 100:
                    self.P2_lose = False

        if self.P1_lose or self.P2_lose:
            self.isTerminal = True
        
        if self.P1_lose:
            self.P2_win = True

        if self.P2_lose:
            self.P1_win = True

    def addChild(self, node):
        self.children.append(node)

    def generateNodeInfo(self):
        string = f"Level:{self.level}:Move:{self.movingPlayer}:"
        string += f"{self.P1name}:{self.P1boardNr}:{self.P1moves}|"
        string += f"{self.P2name}:{self.P2boardNr}:{self.P2moves}|"
    
        if self.isTerminal:
            string += "■"
        
        if self.P1_win:
            string += f"✔{self.P1name}"
        if self.P2_win:
            string += f"✔{self.P2name}"
        
        return string

    def heuristic(self, newMoves, newBoardNr):
        #this is the heuristic function
        # higher score = better node
        # for start, program is going to prioritize highest boardNr
        # possible issue for this: might get fast to 90ish, but not have the right move
        # to finish the game
        return newBoardNr 

    def generateChildren(self, specialCases, level):
        """
            RULES:
            1) each Node can have 0,1,2,3,4,5 or 6 children
        """

        if self.isTerminal and  (self.P1_win  or  self.P2_win):
            return
        
        
        if (not self.P1_lose) and self.P1name == self.movingPlayer:
            for move in self.P1moves:
                if self.P1boardNr + move <= 100:
                    
                    #init data for next node
                    P1newBoardNr = self.P1boardNr + move
                    if P1newBoardNr in list(specialCases.keys()):
                        P1newBoardNr = specialCases[P1newBoardNr]

                    P1newMoves = deepcopy(self.P1moves)
                    P1newMoves.remove(move)
                    score = self.heuristic(P1newMoves, P1newBoardNr)
                    node = Node(P1newMoves, self.P1name, P1newBoardNr, self.P2moves,
                                self.P2name, self.P2boardNr, self.P2name, level, score)
                    self.addChild(node)                  
                    
                
        elif (not self.P2_lose) and self.P2name == self.movingPlayer:
            for move in self.P2moves:
                if self.P2boardNr + move <= 100:
                    
                    #init data for next node
                    P2newBoardNr = self.P2boardNr + move
                    if P2newBoardNr in list(specialCases.keys()):
                        P2newBoardNr = specialCases[P2newBoardNr]

                    P2newMoves = deepcopy(self.P2moves)
                    P2newMoves.remove(move)
                    score = self.heuristic(P2newMoves, P2newBoardNr)
                    node = Node(self.P1moves, self.P1name, self.P1boardNr, P2newMoves,
                                self.P2name, P2newBoardNr, self.P1name, level, score)
                    self.addChild(node)

    def generateTree(self, specialCases, level):

        self.generateChildren(specialCases, level)
        level += 1
        for child in self.children:
            if level <= LIMIT:
                child.generateTree(specialCases, level)


    def printTree(self, **kwargs):
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
            child.printTree(file=file, indent=indentCount + 1)

class Tree:
    def __init__(self, specialCases, gameMatrix, root):
        self.specialCases = specialCases
        self.gameMatrix = gameMatrix
        self.root = root

        #self.allNodes = [root]

           
    def generateTree(self):
        self.root.generateTree(self.specialCases,1)
    
    def saveTree(self):
        f = open("tree.txt", "w", encoding="utf-8")
        self.root.printTree(file=f)
        f.close()

