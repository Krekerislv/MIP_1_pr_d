import src.UI
import src.Tree as TreeProcessor

if __name__ == "__main__":
    # Create a new UI object
    ui = src.UI.UI("Snakes and Ladders")

    ui.initPlayer("Player", (0,120,0))
    ui.initPlayer("CPU", (0,0,120))
    ui.updateScoreboard()

    
    #CPU = maximizer
    #Player = minimizer
    ui.chooseFirstPlayer()

    #create start state
    startState = TreeProcessor.Node(ui.Player.moves, ui.Player.name, ui.Player.boardNr,
                                    ui.CPU.moves, ui.CPU.name, ui.CPU.boardNr,
                                    ui.startPlayer.name)

    #create a tree object
    tree = TreeProcessor.Tree(ui.specialCases, ui.posDict, startState)

    #generate tree starting from startState (default depth = 5 (edit at Tree.py line 3))
    tree.generateTree(startState)

    #apply minimax for generated tree (set "minimaxScore" for all nodes)
    
    tree.minimax(startState, maximizing_player=ui.maximizingPlayer)
    tree.saveTree(startState, "tree.txt")
    

    # MAIN game loop
    currentNode = startState
    #a variable that ensures that cpu moves only in nex main loop
    loopHelper = False

    while True:
        
         #check if start state is terminal
        if currentNode.isTerminal:
            #loopHelper = False
            if currentNode.P1_win:
                ui.victor = [currentNode.P1name + " wins!", "Huraay!"]
                currentNode.P1_win = False #avoid loop
                currentNode.P2_win = False #avoid loop
            elif currentNode.P2_win:
                ui.victor = [currentNode.P2name +" wins!", "Ok ):"]
                currentNode.P1_win = False #avoid loop
                currentNode.P2_win = False #avoid loop
            ui.GameOver = True
            ui.update()
            if ui.waitingOnPlayer:
                continue

        #if game is over
        if ui.GameOver:

            ui.waitingOnPlayer = True

            #also resets GameOver
            ui.chooseFirstPlayer()

            #delete old tree and start state
            del startState
            del tree
            print("creating new tree")
            #create start state
            startState = TreeProcessor.Node(ui.Player.moves, ui.Player.name, ui.Player.boardNr,
                                            ui.CPU.moves, ui.CPU.name, ui.CPU.boardNr,
                                            ui.startPlayer.name)
            tree = TreeProcessor.Tree(ui.specialCases, ui.posDict, startState) 
            tree.generateTree(startState)
            tree.minimax(startState,  maximizing_player=ui.maximizingPlayer)
            currentNode = startState

            

        
        #if maximum depth is reached, need to generate more levels
        if not currentNode.children:
            tree.generateTree(currentNode,  limit=currentNode.level + TreeProcessor.LIMIT)
            tree.minimax(currentNode, maximizing_player=ui.maximizingPlayer)
            tree.saveTree(currentNode, "tree"+str(currentNode.level)+".txt")

        #this executes once after player has moved
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
            print(f"newBoardNr: {currentNode.P1boardNr}")
            print(f"new Player moves = {currentNode.P1moves}")
            print(f"new CPU moves = {currentNode.P2moves}")



        if not ui.waitingOnPlayer and loopHelper:
            tmp = currentNode.P2boardNr
            #choose child with highest minimax score. If equal, choose the one with highest CPU's board nr
            currentNode = max(currentNode.children, key= lambda x : [x.minimaxScore, x.P2boardNr ] )
            
            ui.updatePlayerProperties("CPU", currentNode.P2boardNr, currentNode.P2moves)
            ui.updatePlayerProperties("Player", currentNode.P1boardNr, currentNode.P1moves)
            ui.waitingOnPlayer = True
            print(f"\nCPU moved from {tmp} to {currentNode.P2boardNr} (level: {currentNode.level})")
            print(f"new Player moves = {currentNode.P1moves}")
            print(f"new CPU moves = {currentNode.P2moves}")
            

        loopHelper = True
        ui.update()