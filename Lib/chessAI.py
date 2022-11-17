
import Lib.config as config
import random

pieceScore = {"K": 0, "Q":10, "R":5 , "B":3, "N": 3, "P":1}

knightScore = [[1,1,1,1,1,1,1,1],
               [1,2,2,2,2,2,2,1],
               [1,2,3,3,3,3,2,1],
               [1,2,3,4,4,3,2,1],
               [1,2,3,4,4,3,2,1],
               [1,2,3,3,3,3,2,1],
               [1,2,2,2,2,2,2,1],
               [1,1,1,1,1,1,1,1]]

bishopScore = [[3,2,1,1,1,1,2,3],
               [2,3,2,2,2,2,3,2],
               [1,2,3,2,2,3,2,1],
               [1,2,2,3,3,2,2,1],
               [1,2,2,3,3,2,2,1],
               [1,2,3,2,2,3,2,1],
               [2,3,2,2,2,2,3,2],
               [3,2,1,1,1,1,2,3]]

queenScore =  [[1,1,1,2,1,1,1,1],
               [1,2,2,2,2,1,1,1],
               [1,3,3,3,3,3,2,1],
               [1,2,3,3,3,3,2,1],
               [1,2,3,3,3,2,2,1],
               [1,3,3,3,3,3,2,1],
               [1,1,2,2,3,1,1,1],
               [1,1,1,2,1,1,1,1]]

rookScore =   [[2,2,3,4,4,3,2,2],
               [4,4,4,4,4,4,4,4],
               [1,2,2,2,2,2,2,1],
               [1,2,3,3,3,3,2,1],
               [1,2,3,3,3,3,2,1],
               [1,2,2,2,2,2,2,1],
               [4,4,4,4,4,4,4,4],
               [2,2,3,4,4,3,2,2]]

whitePawnScore = [[8,8,8,8,8,8,8,8],
                  [8,8,8,8,8,8,8,8],
                  [5,6,6,7,7,6,6,5],
                  [2,3,3,5,5,3,3,2],
                  [1,2,3,6,6,3,2,1],
                  [1,1,1,4,4,1,1,1],
                  [1,1,1,0,0,1,1,1],
                  [0,0,0,0,0,0,0,0]]

blackPawnScore = [[0,0,0,0,0,0,0,0],
                  [1,1,1,0,0,1,1,1],
                  [1,1,2,4,4,2,1,1],
                  [1,2,3,6,6,3,2,1],
                  [2,3,3,5,5,3,3,2],
                  [5,6,6,7,7,6,6,5],
                  [8,8,8,8,8,8,8,8],
                  [8,8,8,8,8,8,8,8]]

KingScore = [[1,2,4,0,0,0,4,1],
             [0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,0],
             [0,0,0,0,0,0,0,0],
             [1,2,4,0,0,0,4,1]]

piecePositionScores = {'N':knightScore, 'B':bishopScore, 'Q':queenScore, 'R':rookScore, 'wP':whitePawnScore, 'bP':blackPawnScore, "K":KingScore}



CHECMATE = 1000
STALEMATE = 0
DEPTH = config.AI_DEPTH

def findRandomMove(validMoves):
    return validMoves[random.randint(0,len(validMoves)-1)]


def findBestMove(gs, validMoves, returnQueue):
    global nextMove 
    nextMove = None
    random.shuffle(validMoves)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECMATE, CHECMATE, 1 if gs.whiteToMove else -1)
    
    #findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    
    #this is for threading if you not using threding put return nextMove
    returnQueue.put(nextMove)



def findMoveMinMax(gs,validMoves,depth,whiteToMove):
    global nextMove
    
    #fixe leter
    random.shuffle(validMoves)
    
    
    if depth == 0:
        return scoreBoard(gs)
    if whiteToMove:
        maxScore = -CHECMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs,nextMoves,depth-1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH: 
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs,nextMoves,depth-1,True)
            if score < minScore:
                minScore = score
                if depth == DEPTH: 
                    nextMove = move
            gs.undoMove()
        return minScore



def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore



def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    
    maxScore = -CHECMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                print(move, score)
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore
        


    
def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECMATE #Balck wins
        else:
            return CHECMATE #white wins
    elif gs.staleMate:
        return STALEMATE
    
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            
            if square != "--":
                piecePositionScore = 0
                if square[1] == 'P':
                    #for pawns 
                    piecePositionScore = piecePositionScores[square][row][col]
                else:
                    #all the other pieces
                    piecePositionScore = piecePositionScores[square[1]][row][col] + 1
                
                if square[0] == "w":
                    score += pieceScore[square[1]] + piecePositionScore * 0.15
                elif square[0] == "b":
                    score -= pieceScore[square[1]] + piecePositionScore * 0.15
    return score
