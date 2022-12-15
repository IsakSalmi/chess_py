import sys
from multiprocessing import Process, Queue
import Lib.ChessEngine as ChessEngine
import Lib.config as config
import pygame as p
import Lib.chessAI as chessAI
import Lib.StockFish as SF


p.init()

BOARD_WIDTH = BOARD_HEIGHT = config.BOARD_WIDTH
DIMENTION = config.DIMENTION  # 8*8 CHESS BOARD
MOVE_LOG_PANEL_WIDTH = config.LOG_BOARD_WIDTH
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
SQ_SIZE = BOARD_HEIGHT // DIMENTION
MAX_FPS = config.MAX_FPS
IMAGES = {}

'''
Initialise the global dictionary of images. This will be called exactly once in the main
'''
def loadImages():
    pieces = ['bP', 'bR', 'bN', 'bB', 'bQ', 'bK', 'wP', 'wR', 'wN', 'wB', 'wQ', 'wK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(config.IMAGE_FOLDER + piece + ".png"), (SQ_SIZE, SQ_SIZE))


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
    loadImages()  # only do this once -> before the while loop
    runningGame = True
    sqSelected = ()  # no sq is selected initially, keep track of the last click by the user -> (tuple : (row,col))
    playerClicks = []  # contains players clicks => [(6,4),(4,4)]  -> pawn at (6,4) moved 2 steps up on (4,4)
    
    playerOne = False
    playerTwo = False
    
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
                    playerTwo = False
                    start = False 
                elif  (BOARD_WIDTH-60)/2< p.mouse.get_pos()[0] < (BOARD_WIDTH-60)/2 + 100 and 140 < p.mouse.get_pos()[1] < 160:
                    playerOne = True
                    playerTwo = True
                    start = False 
                elif  (BOARD_WIDTH-60)/2< p.mouse.get_pos()[0] < (BOARD_WIDTH-60)/2 + 100 and 180 < p.mouse.get_pos()[1] < 200:
                    playerOne = False
                    playerTwo = True
                    start = False 
                elif  (BOARD_WIDTH-60)/2< p.mouse.get_pos()[0] < (BOARD_WIDTH-60)/2 + 100 and 220 < p.mouse.get_pos()[1] < 240:
                    playerOne = False
                    playerTwo = False
                    start = False 
        drawStartScreen(screen)
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
            
            """
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
                moveMade = True
                AIThinking = False 
            """    
                
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

        drawGameState(screen, gs, sqSelected, validMoves, moveLogFont)

        # Print Checkmate
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawEndGameText(screen, "Black Won by Checkmate!");
            else:
                drawEndGameText(screen, "White Won by Checkmate!");

        # Print Stalmate
        if gs.staleMate:
            gameOver = True
            drawEndGameText(screen, "Draw due to Stalemate!")

        clock.tick(MAX_FPS)
        p.display.flip()


'''
responsible for all the graphics in the game
'''
def drawStartScreen(screen):
    drawBoard(screen)
    drawButton(screen,"1P vs AI",(BOARD_WIDTH-60)/2,100,100,20)
    drawButton(screen,"1P vs P2",(BOARD_WIDTH-60)/2,140,100,20)
    drawButton(screen,"AI vs P2",(BOARD_WIDTH-60)/2,180,100,20)
    drawButton(screen,"AI vs AI",(BOARD_WIDTH-60)/2,220,100,20)
    
    
def drawGameState(screen, gs, selectedSquare, validMoves,moveLogFont):
    drawBoard(screen)  # draw squares on board (should be called before drawing anything else)
    highlightSquares(screen, gs, selectedSquare, validMoves)
    drawPieces(screen, gs.board)  # draw pieces on the board
    drawMoveLog(screen, gs, moveLogFont) #draws the movelog


'''
draw the squares on the board
'''
def drawBoard(screen):
    global colors
    colors = [config.BOARD_COLOR_LIGHT, config.BOARD_COLOR_DARK]
    for r in range(DIMENTION):
        for c in range(DIMENTION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(SQ_SIZE * c, SQ_SIZE * r, SQ_SIZE, SQ_SIZE))



'''
For highlighting the correct sq. of selected piece and the squares it can move to
'''
def highlightSquares(screen, gs, selectedSquare, validMoves):
    if selectedSquare != ():
        r, c = selectedSquare
        r1, c1 = r, c
        enemyColor = 'b' if gs.whiteToMove else 'w'
        allyColor = 'w' if gs.whiteToMove else 'b'
        if gs.board[r][c][0] == allyColor:
            # Highlighting the selected Square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value -> 0 : 100% transparent | 255 : 100% Opaque
            s.fill(p.Color('red'))
            screen.blit(s, (c1 * SQ_SIZE, r1 * SQ_SIZE))

            # Highlighting the valid move squares
            s.fill(p.Color('red'))

            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    endRow = move.endRow
                    endCol = move.endCol
                    drawEndRow, drawEndCol = endRow, endCol
                    if gs.board[endRow][endCol] == '--' or gs.board[endRow][endCol][0] == enemyColor:
                        screen.blit(s, (drawEndCol * SQ_SIZE, drawEndRow * SQ_SIZE))


'''
	Draw the pieces on the board using ChessEngine.GameState.board.
'''
def drawPieces(screen, board):
    for r in range(DIMENTION):
        for c in range(DIMENTION):
            r1, c1 = r, c
            piece = board[r1][c1]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(SQ_SIZE * c, SQ_SIZE * r, SQ_SIZE, SQ_SIZE))
                

def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color(config.MOVE_LOG_COLOR), moveLogRect)
    moveLog = gs.moveLog
    moveText = []
    
    for i in range(0,len(moveLog),2):
        moveString = str(i//2 + 1) + ". " +str(moveLog[i]) + ' '
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1]) + ' '
        moveText.append(moveString)
    
    #fixe so you can change to diffrent format
    movesPerRow = 3
    padding = 5
    lineSpace = 4
    textY = padding
    
    for i in range(0, len(moveText), movesPerRow):
        text = ''
        for j in range(movesPerRow):
            if i + j < len(moveText):
                text += moveText[i+j]
        textObject = font.render(text, True, p.Color(config.MOVE_LOG_COLOR_NOTATION))
        textLocation = moveLogRect.move(padding,textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpace


'''
To wrtie some text in the middle of the screen!
'''
def drawEndGameText(screen, text):
    #  Font Name  Size Bold  Italics
    font = p.font.SysFont('Helvitica', 32, True, False)
    textObject = font.render(text, 0, p.Color('White'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))
    
def drawButton(screen,text,x1,y1,x2,y2):
    font = p.font.SysFont('Helvitica', 30, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(x1, y1, x2, y2)
    p.draw.rect(screen,p.Color("Gray"),textLocation)
    screen.blit(textObject, textLocation)


if __name__ == '__main__':
    main()
