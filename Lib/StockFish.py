from stockfish import Stockfish
import Lib.config as config


class ChessAI_S():
    def __init__(self):
        self.stockfish = Stockfish(path = 'Lib/stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe')
        self.stockfish.set_depth(config.STOCFICH_DEPTH)
        self.stockfish.set_elo_rating(config.STOCFICH_ELO)
        
    def getBestMove(self,validMove):
        move = self.stockfish.get_best_move()
        for Move in validMove:
            if Move.getChessNotation() == move:
                return Move
        return None
        
    def MakeMove_s(self,Move):
        self.stockfish.make_moves_from_current_position([Move.getChessNotation()])








