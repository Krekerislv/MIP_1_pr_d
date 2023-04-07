import os
import pygame
import sys
#set working directory to script dir
#this allows to use relateive directories without going insane
os.chdir(os.path.split(__file__)[0])

class Player:
    def __init__(self, name, gameMatrix, boardNr, radius, color, window, specialCases):
        self.name = name
        self.gameMatrix = gameMatrix
        self.boardNr = boardNr
        self.pos = self.gameMatrix[boardNr]
        self.radius = radius
        self.color = color
        self.window = window
        self.moves = [1,2,3,4,5,6]
        self.selected = False
        self.allowMove = False #controls player turns
        self.canMove = True #indicates if possible moves are available
        self.specialCases = specialCases
        self.takenSpecialCase = None #endpoint
        self.draw()  
    
    def draw(self):
        if self.selected:
            pygame.draw.circle(self.window, (120,0,0),  self.pos,  self.radius)
        else:
            pygame.draw.circle(self.window, self.color,  self.pos,  self.radius)

    def updatePos(self, newBoardNr, takenSpecialCase=None):
        rtrnFlag = False
        move = newBoardNr - self.boardNr
        if move in self.moves:
            self.boardNr = newBoardNr
            self.pos = self.gameMatrix[self.boardNr]

            if takenSpecialCase:
                if self.boardNr in list(self.specialCases):
                    if not takenSpecialCase == self.specialCases[self.boardNr]:
                        self.boardNr = self.specialCases[self.boardNr]
                        self.pos = self.gameMatrix[self.boardNr]

            elif self.boardNr in list(self.specialCases):
                self.boardNr = self.specialCases[self.boardNr]
                self.pos = self.gameMatrix[self.boardNr]
                

            self.moves.remove(move)
            if len(self.moves) == 0:
                self.moves = [1,2,3,4,5,6]
            rtrnFlag = True
        else:
            rtrnFlag = False

        self.canMove = False
        for i in self.moves:
            if self.boardNr + i <= 100:
                self.canMove = True
        
        return rtrnFlag
    
    def drawAvailableMoves(self):
        for i in self.moves:
            if self.boardNr + i <= 100:
                pygame.draw.circle(self.window, (30,30,30),  self.gameMatrix[self.boardNr + i],  5)

    def setDefault(self):
        self.boardNr = 1
        self.pos = self.gameMatrix[1]
        self.moves = [1,2,3,4,5,6]
        self.selected = False
        self.canMove = True
        self.allowMove = False

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

        #setup players:
        self.posDict, self.gameGrid = self.generatePosMatrix()

        self.P1 = Player("Player", self.posDict, 1, 15, (0,150,0), self.window, self.specialCases)
        self.P2 = Player("CPU", self.posDict, 1, 15, (0,125,255), self.window, self.specialCases)

        # Set up the background for the text at the bottom
        self.text_bg = pygame.Surface((self.WIDTH, self.scoreBoardHeight))
        self.text_bg.fill((0, 0, 0))
        self.updateScoreboard()

        self.victor = None
        self.mouseOn_ok_sur = False
        self.mouseOn_ch1_sur = False
        self.mouseOn_ch2_sur = False
        
        #get start player before the loop in main.py starts
        self.startPlayer = None
        while not self.startPlayer:
            self.startPlayer = self.chooseFirstPlayer()
        
        #if player starts the game, wait for move
        self.waitingOnPlayer = False
        if self.startPlayer.name == self.P1.name:
            self.waitingOnPlayer = True
        self.GameOver = False
        
        #a flag that indicates when cpu has made a move
        self.cpuMoveDone = False 

    def updateScoreboard(self):
        # Draw the player position and avalable moves at the bottom
        P1_pos_str = self.font.render(f"{self.P1.name} Position: {self.P1.boardNr}", True, (255, 255, 255))
        P2_pos_str = self.font.render(f"{self.P2.name} Position: {self.P2.boardNr}", True, (255, 255, 255))
        P1_moves_str = self.font.render(f"{self.P1.name} Moves: {', '.join(map(str, self.P1.moves))}", True, (255, 255, 255))
        P2_moves_str = self.font.render(f"{self.P2.name} Moves: {', '.join(map(str, self.P2.moves))}", True, (255, 255, 255))
        self.text_bg.fill((0,0,0))
        self.window.blit(self.text_bg, (0, self.HEIGHT - self.scoreBoardHeight))
        self.window.blit(P1_pos_str, (10, self.HEIGHT - self.scoreBoardHeight))
        self.window.blit(P2_pos_str, (self.WIDTH //2, self.HEIGHT - self.scoreBoardHeight))
        self.window.blit(P1_moves_str, (10, self.HEIGHT - self.scoreBoardHeight//2))
        self.window.blit(P2_moves_str, (self.WIDTH //2, self.HEIGHT - self.scoreBoardHeight//2))

    def handlePlayerChoice(self):
        if self.mouseOn_ch1_sur:
            self.P1.allowMove = True
            self.P2.allowMove = False
            self.mouseOn_ch1_sur = False
            self.GameOver = False
        elif self.mouseOn_ch2_sur:
            self.P1.allowMove = False
            self.P2.allowMove = True
            self.mouseOn_ch2_sur = False
            self.GameOver = False

    def updateP1(self):
        self.P1.drawAvailableMoves()
        if self.P1.updatePos(self.getClickedTile(), self.P2.takenSpecialCase):
            #deselect player after click but only if piece was moved
            self.P1.selected = False
            self.P1.allowMove = False
            self.P2.allowMove = True
            self.waitingOnPlayer = False

    def updateP2(self):
        self.P2.drawAvailableMoves()
        if self.P2.updatePos(self.getClickedTile(), self.P1.takenSpecialCase):
            #deselect player after click but only if piece was moved
            #self.P2.selected = False
            #self.P1.allowMove = True
            #self.P2.allowMove = False
            #FOR DEBUG:
            self.cpuMoveDone = True

    def resetStartState(self):
        self.P1.setDefault()
        self.P2.setDefault()
        self.victor = None
        self.mouseOn_ok_sur = False
        self.startPlayer = None
        while not self.startPlayer:
            self.startPlayer = self.chooseFirstPlayer()
        if self.startPlayer.name == "CPU":
            self.waitingOnPlayer = False
        else:
            self.waitingOnPlayer = True
        self.cpuMoveDone = False
        self.GameOver = False

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
        selPiece = None
        if abs(xPos-self.P1.pos[0]) < self.P1.radius and abs(yPos-self.P1.pos[1]) < self.P1.radius:
            if self.P1.allowMove:
                selPiece = self.P1
        elif abs(xPos-self.P2.pos[0]) < self.P2.radius and abs(yPos-self.P2.pos[1]) < self.P2.radius:
            if self.P2.allowMove:
                selPiece = self.P2

        return selPiece
      
    def showVictoryPopup(self, msg1, msg2):
        #create a popup container
        popUp = pygame.Surface((self.width_popup, self.height_popup))
        popUp.fill((0,0,0))

        #create a surfaces from text
        ok_sur = self.font.render(msg2, True, (0,255,0))
        victory_sur = self.font.render(msg1, True, (255, 255, 255))

        #create trophy object and add it to container
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
        #set both to false
        self.P1.allowMove = False
        self.P2.allowMove = False

        #create a new popup container
        choicePopUp = pygame.Surface((self.width_popup, self.height_popup))
        choicePopUp.fill((0,0,0))
       
        #create surfaces from text
        choise1_surf = self.font.render(self.P1.name, True, (255,255,255))
        choise2_surf = self.font.render(self.P2.name, True, (255,255,255))
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
            choise1_surf = self.font.render(self.P1.name, True, (0,255,0))
        elif self.mouseOn_ch2_sur:
            choise2_surf = self.font.render(self.P2.name, True, (0,255,0))
        
        
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
                    self.P1.allowMove = True
                    return self.P1
                elif self.mouseOn_ch2_sur:
                    self.P2.allowMove = True
                    return self.P2
                else:
                    return None
        pygame.display.update()

    def handleMouseClick(self):
        #process user choice on first player
        if self.GameOver:
            self.handlePlayerChoice()

        #get selected player piece (P1, P2 or None)
        selPlayer = self.getSelectedPlayer()
        if (selPlayer):
            selPlayer.selected = True

        #if player was selected with previous mouse click, move it to clicked tile
        if self.P1.selected:
            self.updateP1()

        if self.P2.selected: #this code is mostly for testing since P2 is cpu
            self.updateP2()
        
        #if player presses button at game end, reset to start state
        if self.mouseOn_ok_sur:
            self.resetStartState()
        
        #deselect piece after move has been made
        if not selPlayer:
            self.P1.selected = False
            self.P2.selected = False
    
    def updateDisplay(self):
        # Update the display
        self.window.blit(self.board_img, (0, 0))
        #draw players and scoreboard
        self.updateScoreboard()
        self.P1.draw()
        self.P2.draw()
        if self.P1.selected:
            self.P1.drawAvailableMoves()
        elif self.P2.selected:
            self.P2.drawAvailableMoves()

    def handleVictory(self):
        #if one of players have finished, end game
        if self.P1.boardNr == 100:
            self.victor = self.P1.name
        elif self.P2.boardNr == 100:
            self.victor = self.P2.name
        if self.victor:
            self.showVictoryPopup(f"{self.victor} wins!","Huraay!")
            self.GameOver = True

        #if one of the player runs out of possible moves
        if not self.P1.canMove and not self.victor:
            self.showVictoryPopup(f"{self.P1.name} loses!", "Ok ):" )
            self.GameOver = True
        if not self.P2.canMove and not self.victor:
            self.showVictoryPopup(f"{self.P1.name} wins!", "Huraay!" )
            self.GameOver = True

    #if 2 players can access same tile, prevent that
    def handlePlayerMoves(self):
        for moveP1 in self.P1.moves:
            #case 1: it can be directly equal to P2 boardNr
            if self.P1.boardNr + moveP1 == self.P2.boardNr:
                self.P1.moves.remove(moveP1)
            
        #case 2: P2 is at specialCase endpoint:
        if self.P2.boardNr in list(self.specialCases.values()):
            self.P2.takenSpecialCase = self.P2.boardNr
        else:
            self.P2.takenSpecialCase = None

        for moveP2 in self.P2.moves:
            #case 1: it can be directly equal to P2 boardNr
            if self.P2.boardNr + moveP2 == self.P1.boardNr:
                self.P2.moves.remove(moveP2)
        
        #case 2: P1 is at specialCase endpoint:
        if self.P1.boardNr in list(self.specialCases.values()):
            self.P1.takenSpecialCase = self.P1.boardNr
        else:
            self.P1.takenSpecialCase = None

        
            

    def update(self):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handleMouseClick()

        self.handlePlayerMoves()

        #if 2 players are at the same tile, move them apart to avoid overlapping
        if self.P1.pos == self.P2.pos:
            x, y = self.P1.pos
            space = 20
            self.P1.pos = (x-space,y)
            self.P2.pos = (x+space,y)

        if self.cpuMoveDone:
            #whenever cpu finishes move, this will execute ONCE

            #allow Player to move
            self.P2.selected = False
            self.P1.allowMove = True
            self.P2.allowMove = False
            self.cpuMoveDone = False


        self.updateDisplay()
        self.handleVictory()
        pygame.display.update()