import os
import pygame
import sys
import random
from PARAMS import INITIAL_MOVE_COUNT, CPU_IS_MAXIMIZER

#set working directory to script dir
#this allows to use relateive directories without going insane
os.chdir(os.path.split(__file__)[0])

class Player:
    def __init__(self, name, posDict, boardNr,
                radius, color, window, specialCases,
                rdmMoves = False):
        self.name = name
        self.posDict = posDict
        self.boardNr = boardNr
        self.pos = self.posDict[boardNr]
        self.radius = radius
        self.color = color
        self.window = window
        self.rdmMoves = rdmMoves
        self.moves = []
        if self.rdmMoves:
            #generate RANDOM_MOVE_LENGTH moves (only first set of moves)
            #after player runs out of these moves, they will be set to 1,2,3,4
            while len(self.moves) != INITIAL_MOVE_COUNT : self.moves.append(random.randint(1,6))
        else:
            self.moves = [i for i in range(1, INITIAL_MOVE_COUNT+1)]
        self.selected = False
        self.allowMove = False #controls player turns
        self.specialCases = specialCases
        self.takenSpecialCase = None #endpoint
        self.draw()  
    
    def draw(self):
        if self.selected:
            pygame.draw.circle(self.window, (120,0,0),  self.pos,  self.radius)
        else:
            pygame.draw.circle(self.window, self.color,  self.pos,  self.radius)

    def updatePos(self, newBoardNr, takenSpecialCase=-1):
        if self.name == "Player": #if player moved, do additional check
            if newBoardNr == self.boardNr:
                return False
        
            move = newBoardNr - self.boardNr
            if move in self.moves:
                if newBoardNr in list(self.specialCases.keys()):
                    if  takenSpecialCase != self.specialCases[newBoardNr]:
                        newBoardNr = self.specialCases[newBoardNr]
                
                self.pos = self.posDict[newBoardNr]
                self.boardNr = newBoardNr
                return True
        else:      
            self.pos = self.posDict[newBoardNr]
            self.boardNr = newBoardNr
                
        return False
    
    def drawAvailableMoves(self):
        for i in self.moves:
            if self.boardNr + i <= 100:
                pygame.draw.circle(self.window, (30,30,30),  self.posDict[self.boardNr + i],  5)

    def setDefault(self):
        self.boardNr = 1
        self.pos = self.posDict[1]
        self.moves = []
        if self.rdmMoves:
            #generate RANDOM_MOVE_LENGTH moves (only first set of moves)
            #after player runs out of these moves, they will be set to 1,2,3,4
            while len(self.moves) != INITIAL_MOVE_COUNT : self.moves.append(random.randint(1,6))
        else:
            self.moves = [i for i in range(1, INITIAL_MOVE_COUNT+1)]
        self.selected = False

class UI:
    def __init__(self, title):
        #snakes and ladders
        self.specialCases = {
            4:25,
            21:39,
            29:74,
            30:7,
            43:76,
            47:15,
            56:19,
            63:80,
            71:89,
            73:51,
            82:42,
            92:75,
            98:55
        }

        # Set up the game window
        self.WIDTH = 1000
        self.HEIGHT = 800
        self.width_popup = 320
        self.height_popup = 240
        self.scoreBoardHeight = 60
        self.imgHeight = self.HEIGHT - self.scoreBoardHeight
        self.title = title
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))#, pygame.RESIZABLE)
        pygame.display.set_caption(self.title)

        # Load the game board image and draw it on window
        self.board_img = pygame.image.load("img/game_board.png")

        self.board_img = pygame.transform.scale(self.board_img, (self.WIDTH, self.imgHeight))
        self.window.blit(self.board_img, (0, 0))


        # Set up the font for the player points and moves
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 24)

        #posDict: key = boarNr, value = position (pixels)
        #gameGrid 2d array containig respective tile nr for each mouse click: 
        self.posDict, self.gameGrid = self.generatePosMatrix()
       
        #set init state for GameOver flag
        self.GameOver = False

        #set start player to None
        self.startPlayer = None
        
        #winning player
        self.victor = None
        
        #a flag that indicates when player has made a move
        self.cpuMoveDone = False 
        self.playerMoveDone = False
        
        #flag that can be set from main that let's code know, which is the maximizing player
        self.maximizingPlayerStarts = None # true - maximizing player starts, false - minimizing player starts

        # Set up the background for the text at the bottom
        self.text_bg = pygame.Surface((self.WIDTH, self.scoreBoardHeight))
        self.text_bg.fill((0, 0, 0))


        self.mouseOn_ok_sur = False #flag for when game end message is clicked
        self.mouseOn_ch1_sur = False #flag for when player chooses Player as starting player
        self.mouseOn_ch2_sur = False #flag for when player chooses CPU as starting player
        
    def updateScoreboard(self):
        # Draw the player position and avalable moves at the bottom
        Player_pos_str = self.font.render(f"{self.Player.name} Position: {self.Player.boardNr}", True, (255, 255, 255))
        CPU_pos_str = self.font.render(f"{self.CPU.name} Position: {self.CPU.boardNr}", True, (255, 255, 255))
        Player_moves_str = self.font.render(f"{self.Player.name} Moves: {', '.join(map(str, sorted(self.Player.moves)))}", True, (255, 255, 255))
        CPU_moves_str = self.font.render(f"{self.CPU.name} Moves: {', '.join(map(str, sorted(self.CPU.moves)))}", True, (255, 255, 255))
        self.text_bg.fill((0,0,0))
        self.window.blit(self.text_bg, (0, self.HEIGHT - self.scoreBoardHeight))
        self.window.blit(Player_pos_str, (10, self.HEIGHT - self.scoreBoardHeight))
        self.window.blit(CPU_pos_str, (self.WIDTH //2, self.HEIGHT - self.scoreBoardHeight))
        self.window.blit(Player_moves_str, (10, self.HEIGHT - self.scoreBoardHeight//2))
        self.window.blit(CPU_moves_str, (self.WIDTH //2, self.HEIGHT - self.scoreBoardHeight//2))

    def resetStartState(self):
        self.Player.setDefault()
        self.CPU.setDefault()
        self.mouseOn_ok_sur = False
        self.startPlayer = None
        self.cpuMoveDone = False
        self.victor = None

    def generatePosMatrix(self):
        width = 10
        height = 10
        board_pos = {}
        board_grid = [[0 for col in range(width)] for row in range(height)]
        
        spacingX = 100
        spacingY = 74
        nr = 1
        rang = list(range(width))
        for y in reversed(range(height)):
            for x in rang:
                pos = (int(spacingX/2 + x*spacingX), int(spacingY/2 + y*spacingY))
                board_pos[nr] = pos
                board_grid[height-1-y][x] = nr
                nr += 1
            rang.reverse()
        return board_pos, board_grid

    def getClickedTile(self):
        mousePos = pygame.mouse.get_pos()
        x = 100
        y = 74
        xPos = (mousePos[0] // x)
        yPos = 9 - (mousePos[1] // y)
        return self.gameGrid[yPos][xPos]

    def getSelectedPlayer(self):
        xPos, yPos = pygame.mouse.get_pos()
        if abs(xPos-self.Player.pos[0]) < self.Player.radius and abs(yPos-self.Player.pos[1]) < self.Player.radius:
            if self.Player.allowMove:
                self.Player.selected = True
    
    def showVictoryPopup(self, msg1, msg2):
        self.waitingOnPlayer = True
        #create a popup container
        popUp = pygame.Surface((self.width_popup, self.height_popup))
        popUp.fill((0,0,0))

        #create a surfaces from text
        ok_sur = self.font.render(msg2, True, (0,255,0))
        victory_sur = self.font.render(msg1, True, (255, 255, 255))

        #create trophy object and add it to container
        #trophy image from: https://www.flaticon.com/free-icon/trophy_548484
        trophy_img = pygame.image.load("img/trophy.png")
        trophy_img = pygame.transform.scale(trophy_img, (80, 80))
        popUp.blit(trophy_img, (int(0.7*self.width_popup), self.height_popup//2 - 50))

        #define popUp and ok button positions
        popUp_pos = (self.WIDTH //2 - popUp.get_width()//2, self.HEIGHT //2 - popUp.get_height()//2)
        ok_pos = ((self.width_popup - ok_sur.get_width()) // 2, int(self.height_popup * 0.8))

        #get ok_sur absolute position (in global coordinates)
        ok_sur_abs_pos = (popUp_pos[0] + ok_pos[0], popUp_pos[1] + ok_pos[1])        

        mX, mY = pygame.mouse.get_pos()
        self.mouseOn_ok_sur = mX > ok_sur_abs_pos[0] and mX < ok_sur_abs_pos[0] + ok_sur.get_width() and mY > ok_sur_abs_pos[1] and mY < ok_sur_abs_pos[1] + self.font.get_height()
        if self.mouseOn_ok_sur:
            ok_sur = self.font.render(msg2, True, (0,255,0))
        else:
            ok_sur = self.font.render(msg2, True, (255,255,255))
        
        #add thing to popup container
        popUp.blit(victory_sur, ((int(0.1*self.width_popup), self.height_popup//2 - 50)))
        popUp.blit(ok_sur, ok_pos)
        #add popup to main window
        self.window.blit(popUp, popUp_pos)

    def chooseFirstPlayer(self):
        self.startPlayer = None
        while not self.startPlayer:
            self.Player.allowMove = False
            self.CPU.allowMove = False

            #create a new popup container
            choicePopUp = pygame.Surface((self.width_popup, self.height_popup))
            choicePopUp.fill((0,0,0))
        
            #create surfaces from text
            choise1_surf = self.font.render(self.Player.name, True, (255,255,255))
            choise2_surf = self.font.render(self.CPU.name, True, (255,255,255))
            question_surf = self.font.render("Choose first player!", True, (200,200,0))

            #define popUp position
            popUp_pos = (self.WIDTH //2 - choicePopUp.get_width()//2, self.HEIGHT //2 - choicePopUp.get_height()//2)
            #define text surfaces' positions
            choise1_pos = ((choicePopUp.get_width() - 2*choise1_surf.get_width() - choise1_surf.get_width())//2, choicePopUp.get_height()//2 )
            choise2_pos = ((choicePopUp.get_width() + 2*choise1_surf.get_width() - choise2_surf.get_width())//2, choicePopUp.get_height()//2 )
            question_pos = ((choicePopUp.get_width() - question_surf.get_width())//2, choicePopUp.get_height()//5 )

            #get choice 1 and 2 global coordinates
            ch1_abs_pos = (popUp_pos[0] + choise1_pos[0], popUp_pos[1] + choise1_pos[1])
            ch2_abs_pos = (popUp_pos[0] + choise2_pos[0], popUp_pos[1] + choise2_pos[1])

            mX, mY = pygame.mouse.get_pos()

            #check if mouse is hovering over buttons
            self.mouseOn_ch1_sur = mX > ch1_abs_pos[0] and mX < ch1_abs_pos[0] + choise1_surf.get_width() and mY > ch1_abs_pos[1] and mY < ch1_abs_pos[1] + self.font.get_height()
            self.mouseOn_ch2_sur = mX > ch2_abs_pos[0] and mX < ch2_abs_pos[0] + choise2_surf.get_width() and mY > ch2_abs_pos[1] and mY < ch2_abs_pos[1] + self.font.get_height()
            
            #if mouse is hovering over button, change color
            if self.mouseOn_ch1_sur:
                choise1_surf = self.font.render(self.Player.name, True, (0,255,0))
            elif self.mouseOn_ch2_sur:
                choise2_surf = self.font.render(self.CPU.name, True, (0,255,0))
            
            
            #add elements to popup container
            choicePopUp.blit(question_surf, question_pos)
            choicePopUp.blit(choise1_surf, choise1_pos)
            choicePopUp.blit(choise2_surf, choise2_pos)

            #add popup to main window
            self.window.blit(choicePopUp, popUp_pos)

            #this is necessary so starting player can be determined before going
            #into while loop in main.py
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.mouseOn_ch1_sur:
                        self.Player.allowMove = True
                        self.waitingOnPlayer = True
                        self.startPlayer = self.Player
                        if CPU_IS_MAXIMIZER:
                            self.maximizingPlayerStarts = False
                        else:
                            self.maximizingPlayerStarts = True  
                        #self.maximizingPlayerStarts = False
                    elif self.mouseOn_ch2_sur:
                        self.Player.allowMove = False
                        self.CPU.allowMove = True
                        self.waitingOnPlayer = False
                        self.startPlayer = self.CPU
                        if CPU_IS_MAXIMIZER:
                            self.maximizingPlayerStarts = True
                        else:
                            self.maximizingPlayerStarts = False
                        #self.maximizingPlayerStarts = True#
            pygame.display.update()
        self.GameOver = False

    def handleMouseClick(self):
        #if player was selected with previous mouse click, move it to clicked tile
        if self.Player.selected:
            self.Player.drawAvailableMoves()
            if self.Player.updatePos(self.getClickedTile(), self.CPU.boardNr):
                self.Player.allowMove = False
                self.waitingOnPlayer = False
                self.playerMoveDone = True
            self.Player.selected = False


        #check if player has been selected
        self.getSelectedPlayer()

        #if player presses button at game end, reset to start state
        if self.mouseOn_ok_sur:
            self.waitingOnPlayer = False
            self.resetStartState()
    
    def updateDisplay(self):
        # Update the display
        self.window.blit(self.board_img, (0, 0))
        #draw players and scoreboard
        self.updateScoreboard()
        self.Player.draw()
        self.CPU.draw()
        if self.Player.selected:
            self.Player.drawAvailableMoves()

    def update(self):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handleMouseClick()

        #if 2 players are at the same tile, move them apart to avoid overlapping (only possible for first tile)
        if self.Player.pos == self.CPU.pos:
            x, y = self.Player.pos
            space = 20
            self.Player.pos = (x-space,y)
            self.CPU.pos = (x+space,y)

        if self.waitingOnPlayer:
            self.Player.allowMove = True
            self.CPU.allowMove = False

        self.updateDisplay()
        if self.victor:
            self.showVictoryPopup(self.victor[0], self.victor[1])
        pygame.display.update()

    def initPlayer(self, name,  color, rdmMoves = False):
        if name == "Player":
            self.Player = Player("Player", self.posDict, 1, 15, color, self.window, self.specialCases, rdmMoves)
        elif name == "CPU":
            self.CPU = Player("CPU", self.posDict, 1, 15, color, self.window, self.specialCases, rdmMoves)
    
    def updatePlayerProperties(self, name, newBoardNr, moves):
        if name == "Player":
            self.Player.moves = moves
        elif name == "CPU":
            self.CPU.boardNr = newBoardNr
            self.CPU.moves = moves
            self.CPU.updatePos(self.CPU.boardNr)

