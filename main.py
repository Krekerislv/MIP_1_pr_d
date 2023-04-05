import src.UI
import src.Tree as TreeProcessor

if __name__ == "__main__":
    # Create a new UI object
    ui = src.UI.UI("Snakes and Ladders")
    

    #create start state
    startState = TreeProcessor.Node(ui.P1.moves, ui.P1.name, ui.P1.boardNr,
                                    ui.P2.moves, ui.P2.name, ui.P2.boardNr,
                                    ui.startPlayer.name, 0)
    
    tree = TreeProcessor.Tree(ui.specialCases, ui.posDict, startState)
    tree.generateTree()
    #tree.saveTree()


    #Game loop
    while True:
        ui.update()
        