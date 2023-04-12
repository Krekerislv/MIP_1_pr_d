import src.UI
import src.Tree as TreeProcessor
from PARAMS import SAVE_TREE, RANDOM_MOVES


if __name__ == "__main__":
    # Create a new UI object
    ui = src.UI.UI("Snakes and Ladders")

    ui.initPlayer("Player", (0,120,0), rdmMoves=RANDOM_MOVES)
    ui.initPlayer("CPU", (0,0,120), rdmMoves=RANDOM_MOVES)
    ui.updateScoreboard()

    #show info window
    ui.showInfo()

    #get player choice
    ui.chooseFirstPlayer()
    
    #create start state
    startState = TreeProcessor.Node(ui.Player.moves, ui.Player.name, ui.Player.boardNr,
                                    ui.CPU.moves, ui.CPU.name, ui.CPU.boardNr,
                                    ui.startPlayer.name, isMax=ui.maximizingPlayerStarts)

    #create a tree object
    tree = TreeProcessor.Tree(ui.specialCases, ui.posDict, startState)

    #generate tree starting from startState
    tree.generateTree(startState)

    #apply minimax for generated tree (set "minimaxScore" for all nodes)
    tree.minimax(startState, ui.maximizingPlayerStarts)
    if SAVE_TREE:
        tree.saveTree(startState, "tree.txt")


    # MAIN game loop
    currentNode = startState
    #a variable that ensures that cpu moves only in next loop iteration
    loopHelper = False
    #======================MAIN LOOP=====================================
    while True:
        #check if start state is terminal
        if currentNode.isTerminal:
            if currentNode.P1_win:
                ui.victor = [currentNode.P1name + " wins!", "Huraay!", currentNode.reason]             
            elif currentNode.P2_win:
                ui.victor = [currentNode.P2name +" wins!", "Ok ):", currentNode.reason]
            
            currentNode.P1_win = False
            currentNode.P2_win = False
            ui.GameOver = True
            ui.update()
            if ui.waitingOnPlayer:
                continue

        #if game is over
        if ui.GameOver:
            ui.waitingOnPlayer = True
            
            #chooseFirstPlayer() also resets GameOver
            ui.chooseFirstPlayer()

            #delete old tree and start state
            del startState
            del tree

            #create a new start state
            startState = TreeProcessor.Node(ui.Player.moves, ui.Player.name, ui.Player.boardNr,
                                            ui.CPU.moves, ui.CPU.name, ui.CPU.boardNr,
                                            ui.startPlayer.name, isMax=ui.maximizingPlayerStarts)
            tree = TreeProcessor.Tree(ui.specialCases, ui.posDict, startState)

            #generate new tree and apply minimax
            tree.generateTree(startState)
            tree.minimax(startState, ui.maximizingPlayerStarts)
            if SAVE_TREE:
                tree.saveTree(startState, "tree.txt")
            currentNode = startState
     
        #if maximum depth is reached, need to generate more levels
        if not currentNode.children:
            tree.generateTree(currentNode,  limit=currentNode.level + TreeProcessor.LIMIT)
            tree.minimax(currentNode, currentNode.isMax)
            if SAVE_TREE:
                tree.saveTree(currentNode, f"tree{currentNode.level}.txt")

        #this executes once after player has moved
        if ui.playerMoveDone:
            loopHelper = False
            tmp = currentNode.P1boardNr
            tmpState = currentNode
            for child in currentNode.children:
                if child.P1boardNr == ui.Player.boardNr:
                    currentNode = child
            
            ui.updatePlayerProperties("Player", ui.Player.boardNr, currentNode.P1moves)
            ui.updatePlayerProperties("CPU", currentNode.P2boardNr, currentNode.P2moves)
            ui.playerMoveDone = False

        #Move CPU:
        if not ui.waitingOnPlayer and loopHelper:
            tmp = currentNode.P2boardNr
            #choose child with highest minimax score. If equal, choose the one with highest CPU's board nr
            currentNode = max(currentNode.children, key= lambda x : [x.minimaxScore, x.P2boardNr ] )
            
            ui.updatePlayerProperties("CPU", currentNode.P2boardNr, currentNode.P2moves)
            ui.updatePlayerProperties("Player", currentNode.P1boardNr, currentNode.P1moves)
            ui.waitingOnPlayer = True

        loopHelper = True
        ui.update()