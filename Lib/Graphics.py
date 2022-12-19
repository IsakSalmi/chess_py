import Lib.config as config
import pygame as p


DIMENTION = config.DIMENTION
BOARD_WIDTH = BOARD_HEIGHT = config.BOARD_WIDTH
SQ_SIZE = BOARD_HEIGHT // DIMENTION
MOVE_LOG_PANEL_WIDTH = config.LOG_BOARD_WIDTH
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
IMAGES = {}




'''
Initialise the global dictionary of images. This will be called exactly once in the main
'''
def loadImages():
    pieces = ['bP', 'bR', 'bN', 'bB', 'bQ', 'bK', 'wP', 'wR', 'wN', 'wB', 'wQ', 'wK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(config.IMAGE_FOLDER + piece + ".png"), (SQ_SIZE, SQ_SIZE))


'''
responsible for all the graphics in the game
'''
def drawStartScreen(screen):
    drawBoard(screen)
    drawButton(screen,"1P vs P2",(BOARD_WIDTH-60)/2,100,100,20)
    drawButton(screen,"1P vs AI",(BOARD_WIDTH-170)/2,140,100,20)
    drawButton(screen,"1P vs SF",(BOARD_WIDTH+60)/2,140,100,20)
    drawButton(screen,"AI vs P2",(BOARD_WIDTH-170)/2,180,100,20)
    drawButton(screen,"SF vs P2",(BOARD_WIDTH+60)/2,180,100,20)
    drawButton(screen,"AI vs SF",(BOARD_WIDTH-60)/2,220,100,20)
    
    
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
