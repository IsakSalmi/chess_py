
print
class GameState():
	def __init__(self):
		# board is a 8*8 2D list
		# each element is a 2 character long string consisting of
		# - lower case (b/w) as color
		# - upper case (R,N,B,Q,K or P) as piece name
		# in case the cell is empty then we store '--'
		self.board = [['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
					  ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
					  ['--', '--', '--', '--', '--', '--', '--', '--'],
					  ['--', '--', '--', '--', '--', '--', '--', '--'],
					  ['--', '--', '--', '--', '--', '--', '--', '--'],
					  ['--', '--', '--', '--', '--', '--', '--', '--'],
					  ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
					  ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

		self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
							  'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
		self.whiteToMove = True
		self.moveLog = []
		# Keeping track of kings to make valid move calculation and castling easier.
		self.whiteKingLocation = (7, 4)
		self.blackKingLocation = (0, 4)

		self.inCheck = False
		self.pins = []
		self.checks = []
		self.checkMate = False
		self.staleMate = False

		# For Enpassant
		self.enPassantPossible = ()  # sq. where enpassant capture can happen
		self.enPassantPossibleLog = [self.enPassantPossible]

		# castling
		self.currentCastlingRights = CastleRights(True, True, True, True)
		self.castleRightsLog = [
			CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs, self.currentCastlingRights.bks, self.currentCastlingRights.bqs)]

	'''
	A function to move pieces on the board and record them. (Won't work for castling, pawn-promotion and en-passant)
	'''
	def makeMove(self, move):
		self.board[move.startRow][move.startCol] = '--'  # empty the start cell
		self.board[move.endRow][move.endCol] = move.pieceMoved  # keep the piece moved on the end cell
		self.moveLog.append(move)  # record the move

		# UPDATE KING'S POSITION
		if move.pieceMoved == 'wK':
			self.whiteKingLocation = (move.endRow, move.endCol)
		if move.pieceMoved == 'bK':
			self.blackKingLocation = (move.endRow, move.endCol)

		# Pawn Promotion
		if move.pawnPromotion:
			promotedPiece = 'Q'
			self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

		# En-Passant
		if move.enPassant:
			self.board[move.startRow][move.endCol] = '--'  # Capturing the Piece

		# Update enPassantPossible Variable
		if move.pieceMoved[1] == 'P' and abs(move.endRow - move.startRow) == 2:  # only on 2 sq. pawn advance
			self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
		else:
			self.enPassantPossible = ()

		# castle Move
		if move.isCastleMove:
			if move.endCol < move.startCol:  # Queen side castle
				self.board[move.endRow][0] = '--'
				self.board[move.endRow][move.endCol + 1] = move.pieceMoved[0] + 'R'
			else:  # King side castle
				self.board[move.endRow][7] = '--'
				self.board[move.endRow][move.endCol - 1] = move.pieceMoved[0] + 'R'
    

		self.enPassantPossibleLog.append(self.enPassantPossible)

		# Castling Rights
		self.updateCastlingRights(move)
		newCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
									   self.currentCastlingRights.bks, self.currentCastlingRights.bqs)
		self.castleRightsLog.append(newCastleRights)

		self.whiteToMove = not self.whiteToMove  # swap the turn

	'''
	Undo a move.
	'''
	def undoMove(self):
		if len(self.moveLog) == 0:
			return
		move = self.moveLog.pop()
		self.board[move.startRow][move.startCol] = move.pieceMoved
		self.board[move.endRow][move.endCol] = move.pieceCaptured
		self.whiteToMove = not self.whiteToMove
		# UPDATE KING'S POSITION
		if move.pieceMoved == 'wK':
			self.whiteKingLocation = (move.startRow, move.startCol)
		if move.pieceMoved == 'bK':
			self.blackKingLocation = (move.startRow, move.startCol)

		# Undo Enpassant Move
		if move.enPassant:
			self.board[move.endRow][move.endCol] = '--'
			self.board[move.startRow][move.endCol] = move.pieceCaptured

		self.enPassantPossibleLog.pop()
		self.enPassantPossible = self.enPassantPossibleLog[-1]
		# UNDO castling rights:
		self.castleRightsLog.pop()  # get rid of last 7. Castling right
		self.currentCastlingRights.wks = self.castleRightsLog[-1].wks  # update current castling right
		self.currentCastlingRights.wqs = self.castleRightsLog[-1].wqs  # update current castling right
		self.currentCastlingRights.bks = self.castleRightsLog[-1].bks  # update current castling right
		self.currentCastlingRights.bqs = self.castleRightsLog[-1].bqs  # update current castling right
  
		self.checkMate = False
		self.staleMate = False

		# UNDO CASTLING MOVE:
		if move.isCastleMove:
			if move.endCol < move.startCol:  # Queen Side Castle
				self.board[move.endRow][move.endCol + 1] = '--'
				self.board[move.endRow][0] = move.pieceMoved[0] + 'R'
			else:  # King side castle
				self.board[move.endRow][move.endCol - 1] = '--'
				self.board[move.endRow][7] = move.pieceMoved[0] + 'R'

	'''
	   Updating 7. Castling Right given a Move -> -> when it's a Rook or a King Move
	'''
	def updateCastlingRights(self, move):
		if move.pieceMoved == 'wK':
			self.currentCastlingRights.wqs = False
			self.currentCastlingRights.wks = False

		elif move.pieceMoved == 'bK':
			self.currentCastlingRights.bqs = False
			self.currentCastlingRights.bks = False

		elif move.pieceMoved == 'wR':
			if move.startRow == 7 and move.startCol == 0:
				self.currentCastlingRights.wqs = False
			if move.startRow == 7 and move.startCol == 7:
				self.currentCastlingRights.wks = False
		elif move.pieceMoved == 'bR':
			if move.startRow == 0 and move.startCol == 0:
				self.currentCastlingRights.bqs = False
			if move.startRow == 0 and move.startCol == 7:
				self.currentCastlingRights.bks = False

	''' 
	Get a list of all the valid moves -> the moves that user can actually make. => Considering CHECKS.
	'''
	def getValidMoves(self):
		tempCastlingRights = self.currentCastlingRights
		moves = []
		self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
		if self.whiteToMove:
			kingRow = self.whiteKingLocation[0]
			kingCol = self.whiteKingLocation[1]
		else:
			kingRow = self.blackKingLocation[0]
			kingCol = self.blackKingLocation[1]

		if self.inCheck:
			if len(self.checks) == 1:  # only 1 check -> block check or move king
				moves = self.getAllPossibleMoves()
				# to block check -> move piece btw King and enemy piece Attacking
				check = self.checks[0]
				checkRow = check[0]
				checkCol = check[1]
				pieceChecking = self.board[checkRow][checkCol]  # enemy piece causing the check
				validSquares = []  # sq. to which we can bring our piece to block the check
				# if Night then it must be captured or move the king
				if pieceChecking[1] == 'N':
					validSquares.append((checkRow, checkCol))
				# other pieces can be blockedMoves
				else:
					for i in range(1, 8):
						validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
						validSquares.append(validSquare)
						if validSquare[0] == checkRow and validSquare[1] == checkCol:  # once you reach attacking piece stop.
							break

				# get rid of any move that doesn't block king or capture the piece
				for i in range(len(moves) - 1, -1, -1):
					if moves[i].pieceMoved[1] != 'K':  # move doesn't move King so must block or Capture
						if not (moves[i].endRow, moves[i].endCol) in validSquares:
							moves.remove(moves[i])

			else:  # double check -> must move king
				self.getKingMoves(kingRow, kingCol, moves)

		else:
			moves = self.getAllPossibleMoves()

		if len(moves) == 0:
			if self.inCheck:
				self.checkMate = True
			else:
				self.staleMate = True
		if len(self.moveLog) == 120:
			self.staleMate = True #change to a diffrent losing title2,

		self.currentCastlingRights = tempCastlingRights

		# get 7. Castling Moves
		self.getCastlingMoves(kingRow, kingCol, moves)
		return moves

	'''
	Returns if a player is in check, a list of all pins and list of all checks
	'''
	def checkForPinsAndChecks(self):
		pins = []  # sq. where allied pinned piece is and the direction of pin
		checks = []  # sq. where enemy is attacking
		inCheck = False
		# basic info
		if self.whiteToMove:
			enemyColor = 'b'
			allyColor = 'w'
			startRow = self.whiteKingLocation[0]
			startCol = self.whiteKingLocation[1]
		else:
			enemyColor = 'w'
			allyColor = 'b'
			startRow = self.blackKingLocation[0]
			startCol = self.blackKingLocation[1]
		directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
		for j in range(len(directions)):  # stands for direction => [0,3] -> orthogoal || [4,7] -> diagonal
			d = directions[j]
			possiblePins = ()  # reset possible pins
			for i in range(1, 8):  # stands for number of sq. away
				endRow = startRow + (d[0] * i)
				endCol = startCol + (d[1] * i)
				if 0 <= endRow < 8 and 0 <= endCol < 8:
					endPiece = self.board[endRow][endCol]
					if endPiece[0] == allyColor and endPiece[1] != 'K':  # when we call this function from KingMoves we temp. move king -> this generates a phantom king and actual king is protecting it so we don't want that.
						if possiblePins == ():  # 1st piece that too ally -> might be a pin
							possiblePins = (endRow, endCol, d[0], d[1])
						else:  # 2nd ally piece -> no pins or checks in this direction
							break
					elif endPiece[0] == enemyColor:
						pieceType = endPiece[1]
						if (0 <= j <= 3 and pieceType == 'R') or \
								(4 <= j <= 7 and pieceType == 'B') or \
								(i == 1 and pieceType == 'P') and (
								(enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5)) or \
								(pieceType == 'Q') or \
								(i == 1 and pieceType == 'K'):
							if possiblePins == ():  # no piece blocking, so check
								inCheck = True
								checks.append((endRow, endCol, d[0], d[1]))
								break
							else:  # there exists possibility of pin
								pins.append(possiblePins)
								break
						else:  # enemy piece not applying check
							break
				else:  # OFF BOARD
					break
		# CHECK FOR KNIGHT CHECKS:
		knightMoves = [(-1, -2), (-2, -1), (1, -2), (2, -1), (1, 2), (2, 1), (-1, 2), (-2, 1)]
		for m in knightMoves:
			endRow = startRow + m[0]
			endCol = startCol + m[1]
			if 0 <= endRow <= 7 and 0 <= endCol <= 7:
				endPiece = self.board[endRow][endCol]
				if endPiece[0] == enemyColor and endPiece[1] == 'N':  # enemy knight attacking king
					inCheck = True
					checks.append((endRow, endCol, m[0], m[1]))
		return inCheck, pins, checks

	'''
	Get a list of all possible moves -> Without considering CHECKS
	'''
	def getAllPossibleMoves(self):
		moves = []
		for r in range(len(self.board)):
			for c in range(len(self.board[r])):
				turn = self.board[r][c][0]
				piece = self.board[r][c][1]
				if not (self.whiteToMove ^ (turn == 'w')):
					# if (self.whiteToMove and turn == 'w') or (self.whiteToMove == False and turn == 'b'):
					if piece != '-':
						self.moveFunctions[piece](r, c, moves)  # call appropriate get piece move function
		return moves

	'''
	Get all possible moves for a pawn located at (r,c) and add the moves to the list.
	'''
	def getPawnMoves(self, r, c, moves):
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins) - 1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2], self.pins[i][3])
				self.pins.remove(self.pins[i])
				break

		if self.whiteToMove:
			moveAmount = -1
			startRow = 6
			backRow = 0
			enemyColor = 'b'
		else:
			moveAmount = 1
			startRow = 1
			backRow = 7
			enemyColor = 'w'

		pawnPromotion = False

		# pawn advance
		if self.board[r + moveAmount][c] == '--':  # 1 square pawn advance
			if not piecePinned or pinDirection == (moveAmount, 0):
				if r + moveAmount == backRow:
					pawnPromotion = True
				moves.append(Move((r, c), (r + moveAmount, c), self.board, pawnPromotion=pawnPromotion))
				if r == startRow and self.board[r + (2 * moveAmount)][c] == '--':  # 2 square pawn advance
					moves.append(Move((r, c), (r + (2 * moveAmount), c), self.board))

		# captures to left
		if c - 1 >= 0:
			if not piecePinned or pinDirection == (moveAmount, -1):
				if self.board[r + moveAmount][c - 1][0] == enemyColor:
					if r + moveAmount == backRow:
						pawnPromotion = True
					moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, pawnPromotion=pawnPromotion))
				if (r + moveAmount, c - 1) == self.enPassantPossible:
					moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, enPassant=True))

		# capture to right
		if c + 1 < len(self.board):
			if not piecePinned or pinDirection == (moveAmount, 1):
				if self.board[r + moveAmount][c + 1][0] == enemyColor:
					if r + moveAmount == backRow:
						pawnPromotion = True
					moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, pawnPromotion=pawnPromotion))
				if (r + moveAmount, c + 1) == self.enPassantPossible:
					moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, enPassant=True))

	'''
	Get all possible moves for a Rook located at (r,c) and add the moves to the list.
	'''

	def getRookMoves(self, r, c, moves):
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins) - 1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2], self.pins[i][3])
				if self.board[r][c][1] != 'Q':  # if we remove pin in case of a Queen then it will allow Bishop type moves on Queen.
					self.pins.remove(self.pins[i])
				break
		directions = ((-1, 0), (1, 0), (0, -1), (0, 1))  # up down left right
		enemyColor = 'b' if self.whiteToMove else 'w'  # opponenet's color according to current turn
		for d in directions:
			for i in range(1, 8):
				endRow = r + (d[0] * i)
				endCol = c + (d[1] * i)
				if endRow >= 0 and endRow < len(self.board) and endCol >= 0 and endCol < len(self.board[endRow]):
					if not piecePinned or pinDirection == d or pinDirection == (
							-d[0], -d[1]):  # move towards the pic or away from it
						if self.board[endRow][endCol] == '--':  # Empty square
							moves.append(Move((r, c), (endRow, endCol), self.board))
						elif self.board[endRow][endCol][0] == enemyColor:  # capture opponent's piece
							moves.append(Move((r, c), (endRow, endCol), self.board))
							break
						else:
							break  # same color piece
				else:
					break  # off board

	'''
	Get all possible moves for a Knight located at (r,c) and add the moves to the list.
	'''

	def getKnightMoves(self, r, c, moves):
		piecePinned = False
		for i in range(len(self.pins) - 1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				self.pins.remove(self.pins[i])
				break

		if not piecePinned:  # if a knight is pinned we can't move it any where
			directions = ((-1, -2), (-2, -1), (1, -2), (2, -1), (1, 2), (2, 1), (-1, 2), (-2, 1))
			allyColor = 'w' if self.whiteToMove else 'b'  # opponenet's color according to current turn
			for d in directions:
				endRow = r + d[0]
				endCol = c + d[1]
				if endRow >= 0 and endRow < len(self.board) and endCol >= 0 and endCol < len(self.board[endRow]):
					endPiece = self.board[endRow][endCol]
					if endPiece[0] != allyColor:
						moves.append(Move((r, c), (endRow, endCol), self.board))

	'''
	Get all possible moves for a Bishop located at (r,c) and add the moves to the list.
	'''

	def getBishopMoves(self, r, c, moves):
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins) - 1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2], self.pins[i][3])
				self.pins.remove(self.pins[i])
				break

		directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # (top left) (top right) (bottom left) (bottom right)
		enemyColor = 'b' if self.whiteToMove else 'w'  # opponenet's color according to current turn
		for d in directions:
			for i in range(1, 8):
				endRow = r + (d[0] * i)
				endCol = c + (d[1] * i)
				if endRow >= 0 and endRow < len(self.board) and endCol >= 0 and endCol < len(self.board[endRow]):
					if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
						if self.board[endRow][endCol] == '--':  # Empty Square
							moves.append(Move((r, c), (endRow, endCol), self.board))
						elif self.board[endRow][endCol][0] == enemyColor:  # capture opponent's piece
							moves.append(Move((r, c), (endRow, endCol), self.board))
							break
						else:
							break  # same color piece
				else:
					break  # off board

	'''
	Get all possible moves for a Queen located at (r,c) and add the moves to the list.
	'''
	def getQueenMoves(self, r, c, moves):
		self.getRookMoves(r, c, moves)
		self.getBishopMoves(r, c, moves)

	'''
	Get all possible moves for a King located at (r,c) and add the moves to the list.
	'''
	def getKingMoves(self, r, c, moves):
		directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
		allyColor = 'w' if self.whiteToMove else 'b'  # ally color according to current turn
		for d in directions:
			endRow = r + d[0]
			endCol = c + d[1]
			if endRow >= 0 and endRow < len(self.board) and endCol >= 0 and endCol < len(self.board[endRow]):
				endPiece = self.board[endRow][endCol]
				if endPiece[0] != allyColor:  # not an ally color -> enemy or blank

					# temporarily move the king to the new location
					if allyColor == 'w':
						self.whiteKingLocation = (endRow, endCol)
					if allyColor == 'b':
						self.blackKingLocation = (endRow, endCol)

					# check for check
					inCheck, pins, checks = self.checkForPinsAndChecks()
					# if not check then valid move
					if not inCheck:
						moves.append(Move((r, c), (endRow, endCol), self.board))

					# place king back
					if allyColor == 'w':
						self.whiteKingLocation = (r, c)
					if allyColor == 'b':
						self.blackKingLocation = (r, c)

	'''
	Gets the list of all of the king's castling move -> for the king at(r,c);
	'''
	def getCastlingMoves(self, r, c, moves):
		if self.inCheck:
			return  # can't ca
		if (self.whiteToMove and self.currentCastlingRights.wks) or \
				(not self.whiteToMove and self.currentCastlingRights.bks):
			self.getKingSideCastleMoves(r, c, moves)

		if (self.whiteToMove and self.currentCastlingRights.wqs) or \
				(not self.whiteToMove and self.currentCastlingRights.bqs):
			self.getQueenSideCastleMoves(r, c, moves)

	def getKingSideCastleMoves(self, r, c, moves):
		if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
			if not self.isUnderAttack(r, c + 1) and not self.isUnderAttack(r, c + 2):
				moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

	def getQueenSideCastleMoves(self, r, c, moves):
		if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
			if not self.isUnderAttack(r, c - 1) and not self.isUnderAttack(r, c - 2):
				moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))




	def isUnderAttack(self, r, c):
		#here we move away from the square we want to calculate threat from
		allyColor = 'w' if self.whiteToMove else 'b'
		enemyColor = 'b' if self.whiteToMove else 'w'
		directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
		undetAttack = False
		for j in range(len(directions)):  # stands for direction => [0,3] -> orthogoal || [4,7] -> diagonal
			d = directions[j]
			for i in range(1, 8):  # stands for number of sq. away
				endRow = r + (d[0] * i)
				endCol = c + (d[1] * i)
				if 0 <= endRow < 8 and 0 <= endCol < 8:
					endPiece = self.board[endRow][endCol]
					if endPiece[0] == allyColor:
						break
					elif endPiece[0] == enemyColor:
						pieceType = endPiece[1]
						if (0 <= j <= 3 and pieceType == 'R') or \
								(4 <= j <= 7 and pieceType == 'B') or \
								(i == 1 and pieceType == 'P') and (
								(enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5)) or \
								(pieceType == 'Q') or \
								(i == 1 and pieceType == 'K'):

							return True
						else:  # enemy piece not applying check
							break
				else:  # OFF BOARD
					break
		if undetAttack:
			return True
		# CHECK FOR KNIGHT CHECKS:
		knightMoves = [(-1, -2), (-2, -1), (1, -2), (2, -1), (1, 2), (2, 1), (-1, 2), (-2, 1)]
		for m in knightMoves:
			endRow = r + m[0]
			endCol = c + m[1]
			if 0 <= endRow <= 7 and 0 <= endCol <= 7:
				endPiece = self.board[endRow][endCol]
				if endPiece[0] == enemyColor and endPiece[1] == 'N':  # enemy knight attacking king
					return True
		return False


class CastleRights:

	def __init__(self, wks, wqs, bks, bqs):
		self.wks = wks
		self.wqs = wqs
		self.bks = bks
		self.bqs = bqs

	'''
	Overloading the __str__ function to print the 7. Castling Rights Properly
	'''

	def __str__(self):
		return ("7. Castling Rights(wk, wq, bk, bq) : " + str(self.wks) + " " + str(self.wqs) + " " + str(
			self.bks) + " " + str(self.bqs))


class Move():
	# maps keys to values
	# For converting (row, col) to Chess Notations => (0,0) -> a8
	ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
				   "5": 3, "6": 2, "7": 1, "8": 0}
	rowsToRanks = {v: k for k, v in ranksToRows.items()}
	filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
				   "e": 4, "f": 5, "g": 6, "h": 7}
	colsToFiles = {v: k for k, v in filesToCols.items()}

	def __init__(self, startSq, endSq, board, enPassant=False, pawnPromotion=False, isCastleMove=False):
		self.startRow = startSq[0]
		self.startCol = startSq[1]
		self.endRow = endSq[0]
		self.endCol = endSq[1]
		self.pieceMoved = board[self.startRow][self.startCol]  # can't be '--'
		self.pieceCaptured = board[self.endRow][self.endCol]  # can be '--' -> no piece was captured

		# Pawn Promotion
		self.pawnPromotion = pawnPromotion

		# EnPassant
		self.enPassant = enPassant
		if enPassant:
			self.pieceCaptured = 'bP' if self.pieceMoved == 'wP' else 'wP'

		# CastleMove
		self.isCastleMove = isCastleMove

		self.isCapture = self.pieceCaptured != '--'
		self.moveId = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

	def getChessNotation(self):
		return self.getFileRank(self.startRow, self.startCol) + self.getFileRank(self.endRow, self.endCol)

	def getFileRank(self, r, c):
		return self.colsToFiles[c] + self.rowsToRanks[r]

	'''
	overriding equal to method
	'''

	def __eq__(self, other):
		return isinstance(other, Move) and self.moveId == other.moveId

	def __str__(self):
		if self.isCastleMove:
			return "O-O" if self.endCol == 6 else "O-O-O"
		endSquare = self.getFileRank(self.endRow,self.endCol)
		if self.pieceMoved[1] == 'p':
			if self.isCapture:
				return self.colsToFiles[self.startCol + "x" + endSquare]
			else:
				return endSquare

		moveString = self.pieceMoved[1]
		if self.isCapture:
			moveString += 'x'
		return moveString + endSquare