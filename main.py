import src.UI
import src.Tree as TreeProcessor

if __name__ == "__main__":
    # Create a new UI object
    ui = src.UI.UI("Snakes and Ladders")

    #Player = maximizer
    #CPU = minimizer
    maximizingPlayer = True
    moveNr = 0
    if ui.startPlayer.name == "CPU":
        ui.waitingOnPlayer = False
        maximizingPlayer = False
    else:
        ui.waitingOnPlayer = True

     #create start state
    startState = TreeProcessor.Node(ui.P1.moves, ui.P1.name, ui.P1.boardNr,
                                    ui.P2.moves, ui.P2.name, ui.P2.boardNr,
                                    ui.startPlayer.name)
    
    tree = TreeProcessor.Tree(ui.specialCases, ui.posDict, startState)
    tree.generateTree(startState)
    tree.minimax(startState, maximizing_player=maximizingPlayer)
    tree.saveTree(startState, "tree.txt")
 

    # MAIN game loop
    
    currentNode = startState
    k = 1 #variable to help keep track of tree generation
    gameReset = False
    while True:
        ui.update()
        
        #handels game end events
        if ui.GameOver and not gameReset:
            print("Game Over!")
            tree.generateTree(startState)
            tree.minimax(startState,  maximizing_player=maximizingPlayer)
            moveNr = 0
            ui.GameOver = False
            ui.waitingOnPlayer = True
            gameReset = True
            ui.victor = None
        
        #setup maximizing player and minimizing player
        if ui.waitingOnPlayer:
            maximizingPlayer = True
            if ui.startPlayer.name == "CPU":
                maximizingPlayer = False

        #if maximum depth is reached, need to generate more levels
        if  currentNode.level == k * TreeProcessor.LIMIT - k:
            print("Expanding tree!")
            tree.generateTree(currentNode,  limit=currentNode.level + TreeProcessor.LIMIT)
            #path = tree.minimax(path[-1], path=path)[1]
            tree.minimax(currentNode, maximizing_player=maximizingPlayer)
            tree.saveTree(currentNode, "tree"+str(currentNode.level)+".txt")
            k += 1
            

        #handles events after player moves
        if ui.playerMoveDone:
            #check current state (is terminal)
            if currentNode.isTerminal:
                ui.GameOver = True
                print("GAME OVER!")
                if currentNode.P1_win:
                    ui.victor = currentNode.P1name
                else:
                    ui.victor = currentNode.P2name
                continue

            gameReset = False
            tmp = currentNode.P1boardNr

            moveNr += 1
            for child in currentNode.children:
                if child.P1boardNr == ui.P1.boardNr:
                    currentNode = child
            print(f"Player going from {tmp} to: {currentNode.P1boardNr}")
            
            ui.playerMoveDone = False
    
            #print(f"Positions according to tree:\nCPU: {currentNode.P2boardNr}, Player: {currentNode.P1boardNr}")


        #moves cpu piece
        if not ui.waitingOnPlayer and not ui.GameOver:
            

            #print(f"Positions according to tree:\nCPU: {currentNode.P2boardNr}, Player: {currentNode.P1boardNr}")
            gameReset = False
            tmp =  currentNode.P2boardNr

            currentNode = min(currentNode.children, key= lambda x : x.minimaxScore )

            #check current state (is terminal)
            if currentNode.isTerminal:
                ui.GameOver = True
                print("GAME OVER!")
                if currentNode.P1_win:
                    ui.victor = currentNode.P1name
                else:
                    ui.victor = currentNode.P2name
                continue

            moveToBoardNr = currentNode.P2boardNr

            CPU_moved = True
            if not ui.P2.updatePos(moveToBoardNr):
                CPU_moved = False
                #position update might fail because piece might have climbed the ladders or slid down a snake
                # have to check for these special cases
                if moveToBoardNr in list(ui.specialCases.values()):
                    moveToBoardNr = list(ui.specialCases.keys())[list(ui.specialCases.values()).index(moveToBoardNr)]
                    CPU_moved = ui.P2.updatePos(moveToBoardNr)

            if CPU_moved:
                print(f"CPU going from {tmp} to: {moveToBoardNr}")
            else:
                print(f"CPU failed going from {tmp} to: {moveToBoardNr}")

            
            moveNr += 1
            
            ui.waitingOnPlayer = True
            ui.cpuMoveDone = True
    
        
