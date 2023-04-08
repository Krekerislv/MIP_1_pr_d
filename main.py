import src.UI
import src.Tree as TreeProcessor

if __name__ == "__main__":
    # Create a new UI object
    ui = src.UI.UI("Snakes and Ladders")

    ui.initPlayer("Player", (0,120,0))
    ui.initPlayer("CPU", (0,0,120))
    ui.updateScoreboard()


    #Player = maximizer
    #CPU = minimizer
    #this flag is true if player(maximizer starts game)
    ui.chooseFirstPlayer()
    maximizingPlayer = True
    if ui.startPlayer.name == ui.CPU.name:
        ui.waitingOnPlayer = False
        maximizingPlayer = False
    else:
        ui.waitingOnPlayer = True

     #create start state
    startState = TreeProcessor.Node(ui.Player.moves, ui.Player.name, ui.Player.boardNr,
                                    ui.CPU.moves, ui.CPU.name, ui.CPU.boardNr,
                                    ui.startPlayer.name)
    
    #create a tree object
    tree = TreeProcessor.Tree(ui.specialCases, ui.posDict, startState)

    #generate tree starting from startState (default depth = 5 (edit at Tree.py line 3))
    tree.generateTree(startState)

    #apply minimax for generated tree (set "minimaxScore" for all nodes)
    tree.minimax(startState, maximizing_player=maximizingPlayer)
    tree.saveTree(startState, "tree.txt")
 

    # MAIN game loop
    #moveNr = 0
    currentNode = startState
   # k = 1 #variable to help keep track of tree generation
    regenTreeFlag = True #flag for tree generation at beginning of game
    #a variable that ensures that cpu moves only in nex main loop
    loopHelper = False

    printFlag = True
    while True:


         #check if start state is terminal
        if currentNode.isTerminal:
            #print("Game Over")
            if currentNode.P1_win:
                ui.victor = [currentNode.P1name + " wins!", "Huraay!"]
            elif currentNode.P2_win:
                ui.victor = [currentNode.P2name +" wins!", "Ok ):"]
            ui.GameOver = True
            ui.update()
            if ui.waitingOnPlayer:
                continue
            print("ova here")

        #if game is over
        if ui.GameOver:
            ui.startPlayer = False
            ui.waitingOnPlayer = True
            if regenTreeFlag:
                print("regen tree")
                tree.generateTree(startState)
                tree.minimax(startState,  maximizing_player=maximizingPlayer)
                currentNode = startState
                regenTreeFlag = False
            
            
            #also resets GameOver
            ui.chooseFirstPlayer()
            
       

        
        #if maximum depth is reached, need to generate more levels
        if printFlag:
            print(f"Checking expansion")
            print(f"current level = {currentNode.level}")
            printFlag = False
        #if  currentNode.level % TreeProcessor.LIMIT == 0 and currentNode.level > 0:
        if not currentNode.children:
            #print("\nExpanding tree!\n")
            tree.generateTree(currentNode,  limit=currentNode.level + TreeProcessor.LIMIT)
            tree.minimax(currentNode, maximizing_player=maximizingPlayer)
            tree.saveTree(currentNode, "tree"+str(currentNode.level)+".txt")
           # k += 1


        if ui.playerMoveDone:
            loopHelper = False
            tmp = currentNode.P1boardNr
            tmpState = currentNode
            for child in currentNode.children:
                if child.P1boardNr == ui.Player.boardNr:
                    print("state updated")       
                    currentNode = child
                print(f"{child.P1boardNr} - {ui.Player.boardNr}")
            if tmpState == currentNode:
                print("Error finding new state for player")
                print(f"Player pos: {ui.Player.boardNr}")
                break
            
            ui.updatePlayerProperties("Player", ui.Player.boardNr, currentNode.P1moves)
            ui.updatePlayerProperties("CPU", currentNode.P2boardNr, currentNode.P2moves)
            ui.playerMoveDone = False
            print(f"\nPlayer moved from {tmp} to {ui.Player.boardNr} (level: {currentNode.level})")
            #print(f"newBoardNr: {currentNode.P1boardNr}")
            print(f"new Player moves = {currentNode.P1moves}")
            print(f"new CPU moves = {currentNode.P2moves}")

            printFlag = True

        if not ui.waitingOnPlayer and loopHelper:
            tmp = currentNode.P2boardNr
            currentNode = min(currentNode.children, key= lambda x : x.minimaxScore )
            
            ui.updatePlayerProperties("CPU", currentNode.P2boardNr, currentNode.P2moves)
            ui.updatePlayerProperties("Player", currentNode.P1boardNr, currentNode.P1moves)
            ui.waitingOnPlayer = True
            print(f"\nCPU moved from {tmp} to {currentNode.P2boardNr} (level: {currentNode.level})")
            print(f"new Player moves = {currentNode.P1moves}")
            print(f"new CPU moves = {currentNode.P2moves}")
            
            printFlag = True

        loopHelper = True
        ui.update()
        