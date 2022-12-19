import sys
from multiprocessing import Process, Queue
import Lib.ChessEngine as ChessEngine
import Lib.config as config
import pygame as p
import Lib.chessAI as chessAI
import Lib.StockFish as SF
import Lib.Graphics as Graphics


p.init()

BOARD_WIDTH = BOARD_HEIGHT = config.BOARD_WIDTH
DIMENTION = config.DIMENTION  # 8*8 CHESS BOARD
MOVE_LOG_PANEL_WIDTH = config.LOG_BOARD_WIDTH
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
SQ_SIZE = BOARD_HEIGHT // DIMENTION
MAX_FPS = config.MAX_FPS

'''
This will be out main driver. It will handle user input and update the graphics.
'''
def main():
    
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('Black'))
    
    moveLogFont = p.font.SysFont('Arial', 12, False, False)
    
    gs = ChessEngine.GameState()
    ChessAI_s = SF.ChessAI_S()
    validMoves = gs.getValidMoves()  # get a list of valid moves.
    moveMade = False  # to check if the user made a move. If true recalculate validMoves.
    Graphics.loadImages()  # only do this once -> before the while loop
    runningGame = True
    sqSelected = ()  # no sq is selected initially, keep track of the last click by the user -> (tuple : (row,col))
    playerClicks = []  # contains players clicks => [(6,4),(4,4)]  -> pawn at (6,4) moved 2 steps up on (4,4)
    
    playerOne = False
    playerTwo = False

    OwnAI_W = False
    OwnAI_B = False

    SF_W = False
    SF_B = False
    
    gameOver = False  # True in case of Checkmate and Stalemate
    
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False
    
    #simple start meney
    start = True
    while start:
        for e in p.event.get():
            if e.type == p.QUIT:
                runningGame = False
                start = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if  (BOARD_WIDTH-60)/2< p.mouse.get_pos()[0] < (BOARD_WIDTH-60)/2 + 100 and 100< p.mouse.get_pos()[1] < 120:
                    playerOne = True
                    playerTwo = True
                    start = False 
                elif  (BOARD_WIDTH-60)/2< p.mouse.get_pos()[0] < (BOARD_WIDTH-170)/2 + 100 and 140 < p.mouse.get_pos()[1] < 160:
                    playerOne = True
                    playerTwo = False
                    OwnAI_B = True
                    start = False 
                elif  (BOARD_WIDTH-60)/2< p.mouse.get_pos()[0] < (BOARD_WIDTH+60)/2 + 100 and 140 < p.mouse.get_pos()[1] < 160:
                    playerOne = True
                    playerTwo = False
                    SF_B = True
                    start = False 
                elif  (BOARD_WIDTH-60)/2< p.mouse.get_pos()[0] < (BOARD_WIDTH-170)/2 + 100 and 180 < p.mouse.get_pos()[1] < 200:
                    playerOne = False
                    playerTwo = True
                    OwnAI_W = True
                    start = False 
                elif  (BOARD_WIDTH-60)/2< p.mouse.get_pos()[0] < (BOARD_WIDTH+60)/2 + 100 and 180 < p.mouse.get_pos()[1] < 200:
                    playerOne = False
                    playerTwo = True
                    SF_W = True
                    start = False   
                elif  (BOARD_WIDTH-60)/2< p.mouse.get_pos()[0] < (BOARD_WIDTH-60)/2 + 100 and 220 < p.mouse.get_pos()[1] < 240:
                    playerOne = False
                    playerTwo = False
                    OwnAI_W = True
                    SF_B = True
                    start = False 
        Graphics.drawStartScreen(screen)
        clock.tick(MAX_FPS)
        p.display.flip()
    
    
    #For the chess game
    while runningGame:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                runningGame = False
                if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
            # MOUSE HANDLERS
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) position of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if (col >= 8) or col < 0:  # Click out of board (on move log panel) -> do nothing
                        continue
                    if sqSelected == (row, col):  # user selected the same sq. twice -> deselect the selecion
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append for both 1st and 2nd click
                        if len(playerClicks) == 2:  # when 2nd click
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    gs.makeMove(validMoves[i])
                                    ChessAI_s.MakeMove_s(validMoves[i])
                                    moveMade = True
                                    playerClicks = []  # reset playerClicks
                                    sqSelected = ()  # reset user clicks
                            if not moveMade:
                                playerClicks = [sqSelected]

            # KEY HANDLERS
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo last move id 'z' is pressed
                    gs.undoMove()
                    gameOver = False
                    moveMade = True  # can do `validMoves = gs.validMoves()` but then if we change function name we will have to change the call at various places.
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:  # reset the game if 'r' is pressed
                    gs = ChessEngine.GameState()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                    validMoves = gs.getValidMoves()
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True

        #AI move finder with threading
        if not gameOver and not humanTurn and not moveUndone:
            if (OwnAI_B and not gs.whiteToMove) or (OwnAI_W and gs.whiteToMove):
                if not AIThinking:
                    AIThinking = True
                    print("thinking.....")
                        
                    #if you are not using threading you only need to set AIMove = findBestMove
                    #and take awhay all the threading parts
                    returnQueue = Queue() #used to pass data betweem threads
                    moveFinderProcess = Process(target=chessAI.findBestMove, args=(gs, validMoves, returnQueue))
                    moveFinderProcess.start()
                            
                if not moveFinderProcess.is_alive():
                    print("done thinking")
                    AIMove = returnQueue.get()
                    if AIMove is None:
                        AIMove = chessAI.findRandomMove(validMoves)
                    gs.makeMove(AIMove)
                    ChessAI_s.MakeMove_s(AIMove)
                    moveMade = True
                    AIThinking = False    
            elif (SF_B and not gs.whiteToMove) or (SF_W and gs.whiteToMove):    
                AIMove = ChessAI_s.getBestMove(validMoves)
                if AIMove is None:
                    AIMove = chessAI.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                ChessAI_s.MakeMove_s(AIMove)
                moveMade = True    
            
        #If a move is made we calculate the new move
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
            moveUndone = False

        Graphics.drawGameState(screen, gs, sqSelected, validMoves, moveLogFont)

        # Print Checkmate
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                Graphics.drawEndGameText(screen, "Black Won by Checkmate!");
            else:
                Graphics.drawEndGameText(screen, "White Won by Checkmate!");

        # Print Stalmate
        if gs.staleMate:
            gameOver = True
            Graphics.drawEndGameText(screen, "Draw due to Stalemate!")

        clock.tick(MAX_FPS)
        p.display.flip()

if __name__ == '__main__':
    main()
