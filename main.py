import src.UI
import src.Tree as TreeProcessor

if __name__ == "__main__":
    # Create a new UI object
    ui = src.UI.UI("Snakes and Ladders")
    

    #create start state
    startState = TreeProcessor.Node(ui.P1.moves, ui.P1.name, ui.P1.boardNr,
                                    ui.P2.moves, ui.P2.name, ui.P2.boardNr,
                                    ui.startPlayer.name, 0, 0)
    
    tree = TreeProcessor.Tree(ui.specialCases, ui.posDict, startState)
    tree.generateTree(startState)
    #tree.saveTree(startState, "tree.txt")

    moveNr = 0
    if ui.startPlayer.name == "CPU":
        ui.waitingOnPlayer = False
    else:
        moveNr = 1

    path = tree.minimax(startState)[1]

    #Game loop
    
    curLevel = 0
    while True:
        ui.update()
        '''
        if ui.GameOver:
            tree.generateTree(startState)
            path = tree.minimax(startState)[1]
            moveNr = 0
            curLevel = 0
            ui.GameOver = False
            ui.waitingOnPlayer = True
            
        
        if not ui.waitingOnPlayer and not ui.GameOver:
            #temp code:
            if moveNr == 0 and ui.startPlayer.name=="CPU":
                moveNr = 1

            moveToBoardNr = path[moveNr].P2boardNr
            print(f"cpu going to: {moveToBoardNr}")
            if not ui.P2.updatePos(moveToBoardNr):
                if moveToBoardNr in list(ui.specialCases.values()):
                    moveToBoardNr = list(ui.specialCases.keys())[list(ui.specialCases.values()).index(moveToBoardNr)]
                    ui.P2.updatePos(moveToBoardNr)

            
            moveNr += 2 #plus 2 to skip player's move level
            curLevel += 2
            if moveNr >= len(path):
                tree.generateTree(path[-1],  limit=len(path) + 5)
                #tree.saveTree(path[-1], "tree"+str(curLevel)+".txt")
                path = tree.minimax(path[-1], path=path)[1]
            ui.waitingOnPlayer = True
            ui.cpuMoveDone = True
    '''
        
